from __future__ import annotations

import logging
from datetime import datetime, timezone

from backend.modules.notificaciones.application.mark_overdue import (
    mark_overdue_recommendations,
)
from backend.modules.notificaciones.application.send_deadline_alerts import (
    send_deadline_alerts,
)

logger = logging.getLogger(__name__)


def run_scheduled_evaluations() -> dict:
    """Ejecuta la evaluación periódica de plazos y vencimientos.

    Es idempotente: las alertas usan claves de idempotencia y el vencimiento se
    registra una sola vez por recomendación. La invoca el comando
    ``manage.py evaluar_plazos`` (cron o servicio programado).
    """
    evaluated_at = datetime.now(timezone.utc)
    alerts = send_deadline_alerts()
    overdue = mark_overdue_recommendations()
    logger.info(
        "Evaluación de plazos completada: alertas=%s, mora=%s", alerts, overdue
    )
    return {
        "evaluated_at": evaluated_at.isoformat(),
        "alertas_vencimiento": alerts,
        "mora": overdue,
        "status": "ok",
    }
