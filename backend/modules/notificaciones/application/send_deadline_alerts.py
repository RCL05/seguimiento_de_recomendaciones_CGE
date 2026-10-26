"""Caso de uso: enviar alertas de vencimiento próximo (≤ 15 días).

Reglas de negocio (RF-011):
- Se dispara cuando faltan 15 días o menos para `fecha_vencimiento_legal`.
- Solo aplica a recomendaciones que NO tienen evidencia aprobada.
- Usa `clave_idempotencia` para impedir envíos duplicados en reintentos.
- Un fallo SMTP registra la notificación como FALLIDA sin revertir la creación.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from django.utils import timezone

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

ALERT_DAYS_THRESHOLD = 15


def send_deadline_alerts() -> dict[str, int]:
    """Evalúa plazos y programa alertas idempotentes para recomendaciones próximas a vencer.

    Retorna un diccionario con contadores de ejecución.
    """
    config = ConfiguracionNotificacion.load()
    if not config.notificaciones_activas:
        return {"scheduled": 0, "skipped": 0, "delivered": 0}

    threshold_days = config.umbral_dias or ALERT_DAYS_THRESHOLD
    now = timezone.localtime()  # America/Guayaquil para lógica de negocio
    threshold_date = now.date() + timedelta(days=threshold_days)

    # Recomendaciones activas próximas a vencer sin evidencia aprobada
    candidates = (
        Recomendacion.objects.filter(
            estado__in=[
                Recomendacion.Estado.PENDIENTE,
                Recomendacion.Estado.EN_PLANIFICACION,
                Recomendacion.Estado.EN_EJECUCION,
                Recomendacion.Estado.RECHAZADA_CORRECCION,
            ],
            fecha_vencimiento_legal__lte=threshold_date,
        )
        .exclude(evidencias__validada=True)
        .select_related("unidad_responsable")
        .prefetch_related("unidad_responsable__usuarios")
        .distinct()
    )

    scheduled = 0
    skipped = 0

    for rec in candidates:
        # Notificar a todos los usuarios ejecutores de la unidad responsable
        recipients = Usuario.objects.filter(
            unidad_org=rec.unidad_responsable,
            rol=Usuario.Rol.EJECUTOR,
            activo=True,
        )
        configured_roles = [
            role
            for role in (config.destinatarios_vencimiento or [])
            if role != Usuario.Rol.EJECUTOR
        ]
        configured_recipients = Usuario.objects.filter(
            rol__in=configured_roles,
            activo=True,
        )

        seen = set()
        for recipient in list(recipients) + list(configured_recipients):
            if recipient.id in seen:
                continue
            seen.add(recipient.id)
            key = f"DEADLINE_ALERT:{rec.id}:{recipient.id}:{threshold_date}"
            notification = schedule_notification(
                recommendation=rec,
                recipient=recipient,
                notification_type="ALERTA_VENCIMIENTO",
                idempotency_key=key,
            )
            if notification is None:
                skipped += 1
                continue
            scheduled += 1
            logger.info("Alerta programada: %s → %s", rec.id, recipient.correo_institucional)

    delivered = deliver_pending_notifications(limit=200)
    logger.info(
        "send_deadline_alerts: candidatas=%d, programadas=%d, omitidas=%d, entregadas=%d",
        candidates.count(),
        scheduled,
        skipped,
        delivered,
    )
    return {"scheduled": scheduled, "skipped": skipped, "delivered": delivered}
