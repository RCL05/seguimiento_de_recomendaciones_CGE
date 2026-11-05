"""Caso de uso: registrar y notificar vencimientos de plazo (RF-012, RF-021).

Decisión del equipo (opción 2): el vencimiento NO cambia el estado de la
recomendación; es un indicador calculado (recomendaciones/domain/vencimiento.py).

Reglas de negocio:
- Una recomendación vencida se registra y notifica una sola vez por ciclo:
  se marca `vencimiento_registrado_en` dentro de transaction.atomic + select_for_update.
- Se notifica a los ejecutores de la unidad y a los roles configurados (UAI, Rectorado).
- La tarea es idempotente y tolerante a reintentos (claves de idempotencia únicas).
- Un fallo SMTP no revierte el registro del vencimiento.
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
from backend.modules.recomendaciones.infrastructure.repositories import anotar_vencimiento
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario

logger = logging.getLogger(__name__)


def mark_overdue_recommendations() -> dict[str, int]:
    """Registra los vencimientos nuevos y programa sus notificaciones. Retorna contadores."""
    today = timezone.localdate()  # America/Guayaquil para lógica de negocio
    config = ConfiguracionNotificacion.load()
    request_id = uuid4()

    pendientes = anotar_vencimiento(
        Recomendacion.objects.filter(vencimiento_registrado_en__isnull=True), today
    ).filter(vencida=True)

    marked = 0
    skipped = 0
    for rec_id in pendientes.values_list("id", flat=True):
        try:
            with transaction.atomic():
                rec = (
                    Recomendacion.objects.select_for_update()
                    .select_related("unidad_responsable")
                    .get(pk=rec_id)
                )
                # Revalidar dentro del bloqueo: otro proceso pudo registrarla o cambiarla.
                still_overdue = (
                    anotar_vencimiento(Recomendacion.objects.filter(pk=rec_id), today)
                    .values_list("vencida", flat=True)
                    .first()
                )
                if rec.vencimiento_registrado_en is not None or not still_overdue:
                    skipped += 1
                    continue

                rec.vencimiento_registrado_en = timezone.now()
                rec.save(update_fields=["vencimiento_registrado_en"])
                record_audit(
                    request_id=request_id,
                    user=None,
                    action="MARK_OVERDUE",
                    entity="recomendacion",
                    entity_id=rec.id,
                    previous_state=rec.estado,
                    new_state=rec.estado,
                    details={
                        "fecha_vencimiento_legal": rec.fecha_vencimiento_legal.isoformat(),
                        "vencida": True,
                    },
                    modulo="notificaciones",
                    resultado="OK",
                )
                _notify_overdue(rec, config)
                marked += 1
                logger.info("Vencimiento registrado para recomendación %s", rec.id)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error al procesar vencimiento de la recomendación %s: %s", rec_id, exc)

    delivered = deliver_pending_notifications(limit=300)
    logger.info(
        "mark_overdue: registradas=%d, omitidas=%d, notificaciones_entregadas=%d",
        marked,
        skipped,
        delivered,
    )
    return {"marked": marked, "skipped": skipped, "delivered": delivered}


def _notify_overdue(rec: Recomendacion, config=None) -> None:
    """Programa notificaciones de mora para todos los roles afectados."""
    config = config or ConfiguracionNotificacion.load()
    if not config.notificaciones_activas:
        return

    configured_roles = [
        role
        for role in (config.destinatarios_mora or [])
        if role != Usuario.Rol.EJECUTOR
    ]
    recipients_qs = Usuario.objects.filter(rol__in=configured_roles, activo=True)
    unit_recipients = Usuario.objects.filter(
        unidad_org=rec.unidad_responsable,
        rol=Usuario.Rol.EJECUTOR,
        activo=True,
    )

    ciclo = rec.vencimiento_registrado_en.date().isoformat()
    seen = set()
    for recipient in list(recipients_qs) + list(unit_recipients):
        if recipient.id in seen:
            continue
        seen.add(recipient.id)
        key = f"MORA:{rec.id}:{recipient.id}:{ciclo}"
        try:
            schedule_notification(
                recommendation=rec,
                recipient=recipient,
                notification_type="EN_MORA",
                idempotency_key=key,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo programar notificación de mora %s: %s", key, exc)
