
"""Caso de uso: marcar recomendaciones vencidas como EN_MORA.

Reglas de negocio (RF-012):
- Solo las recomendaciones con plazo vencido y sin evidencia aprobada pasan a EN_MORA.
- La transición se ejecuta dentro de transaction.atomic con select_for_update.
- Se notifica a la unidad responsable, UAI y Rectorado.
- La tarea es idempotente: si ya está EN_MORA, no hace nada.
- Un fallo SMTP no revierte la transición de negocio.
"""
from __future__ import annotations

import logging
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from backend.core.audit.repository import record_audit
from backend.modules.notificaciones.application.service import (
    deliver_pending_notifications,
    schedule_notification,
)
from backend.modules.notificaciones.infrastructure.preferences_models import (
    ConfiguracionNotificacion,
)
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario

logger = logging.getLogger(__name__)

TRANSITIONABLE_STATES = [
    Recomendacion.Estado.PENDIENTE,
    Recomendacion.Estado.EN_PLANIFICACION,
    Recomendacion.Estado.EN_EJECUCION,
    Recomendacion.Estado.RECHAZADA_CORRECCION,
]


def mark_overdue_recommendations() -> dict[str, int]:
    """Evalúa vencimientos y transiciona recomendaciones a EN_MORA.

    Retorna contadores de ejecución.
    """
    today = timezone.localdate()  # America/Guayaquil para lógica de negocio

    config = ConfiguracionNotificacion.load()

    candidates = (
        Recomendacion.objects.filter(
            estado__in=TRANSITIONABLE_STATES,
            fecha_vencimiento_legal__lt=today,
        )
        .exclude(evidencias__validada=True)
        .distinct()
    )

    marked = 0
    skipped = 0
    request_id = uuid4()

    for rec_id in candidates.values_list("id", flat=True):
        try:
            with transaction.atomic():
                rec = (
                    Recomendacion.objects.select_for_update()
                    .select_related("unidad_responsable")
                    .get(pk=rec_id)
                )
                # Verificar condiciones dentro del lock
                if rec.estado not in TRANSITIONABLE_STATES:
                    skipped += 1
                    continue
                if rec.fecha_vencimiento_legal >= today:
                    skipped += 1
                    continue
                if rec.evidencias.filter(validada=True).exists():
                    skipped += 1
                    continue

                previous = rec.estado
                rec.estado = Recomendacion.Estado.EN_MORA
                rec.save(update_fields=["estado"])

                record_audit(
                    request_id=request_id,
                    user=None,
                    action="MARK_OVERDUE",
                    entity="recommendation",
                    entity_id=rec.id,
                    previous_state=previous,
                    new_state=rec.estado,
                    modulo="notificaciones",
                    resultado="OK",
                )

                # Notificar a Rectorado, UAI y ejecutores de la unidad
                _notify_overdue(rec, today, config)
                marked += 1
                logger.info("Recomendación marcada EN_MORA: %s", rec.id)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error al procesar mora para recomendación %s: %s", rec_id, exc)

    delivered = deliver_pending_notifications(limit=300)
    logger.info(
        "mark_overdue: marcadas=%d, omitidas=%d, notificaciones_entregadas=%d",
        marked,
        skipped,
        delivered,
    )
    return {"marked": marked, "skipped": skipped, "delivered": delivered}


def _notify_overdue(rec: Recomendacion, today, config=None) -> None:
    """Programa notificaciones de mora para todos los roles afectados."""
    config = config or ConfiguracionNotificacion.load()
    if not config.notificaciones_activas:
        return

    configured_roles = [
        role
        for role in (config.destinatarios_mora or [])
        if role != Usuario.Rol.EJECUTOR
    ]
    recipients_qs = Usuario.objects.filter(
        rol__in=configured_roles,
        activo=True,
    )
    unit_recipients = Usuario.objects.filter(
        unidad_org=rec.unidad_responsable,
        rol=Usuario.Rol.EJECUTOR,
        activo=True,
    )

    seen = set()
    for recipient in list(recipients_qs) + list(unit_recipients):
        if recipient.id in seen:
            continue
        seen.add(recipient.id)
        key = f"MORA:{rec.id}:{recipient.id}:{today}"
        try:
            schedule_notification(
                recommendation=rec,
                recipient=recipient,
                notification_type="EN_MORA",
                idempotency_key=key,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo programar notificación de mora %s: %s", key, exc)
