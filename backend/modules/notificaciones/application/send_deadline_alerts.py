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

from django.db import IntegrityError, transaction
from django.utils import timezone

from backend.modules.notificaciones.application.service import (
    deliver_pending_notifications,
    schedule_notification,
)
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario

logger = logging.getLogger(__name__)

ALERT_DAYS_THRESHOLD = 15


def send_deadline_alerts() -> dict[str, int]:
    """Evalúa plazos y programa alertas idempotentes para recomendaciones próximas a vencer.

    Retorna un diccionario con contadores de ejecución.
    """
    now = timezone.localtime()  # America/Guayaquil para lógica de negocio
    threshold_date = now.date() + timedelta(days=ALERT_DAYS_THRESHOLD)

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
        # Notificar también a UAI
        uai_users = Usuario.objects.filter(rol=Usuario.Rol.UAI, activo=True)

        for recipient in list(recipients) + list(uai_users):
            key = f"DEADLINE_ALERT:{rec.id}:{recipient.id}:{threshold_date}"
            try:
                with transaction.atomic():
                    schedule_notification(
                        recommendation=rec,
                        recipient=recipient,
                        notification_type="ALERTA_VENCIMIENTO",
                        idempotency_key=key,
                    )
                scheduled += 1
                logger.info("Alerta programada: %s → %s", rec.id, recipient.correo_institucional)
            except IntegrityError:
                skipped += 1
                logger.debug("Alerta ya existente (idempotente): %s", key)

    delivered = deliver_pending_notifications(limit=200)
    logger.info(
        "send_deadline_alerts: candidatas=%d, programadas=%d, omitidas=%d, entregadas=%d",
        candidates.count(),
        scheduled,
        skipped,
        delivered,
    )
    return {"scheduled": scheduled, "skipped": skipped, "delivered": delivered}
