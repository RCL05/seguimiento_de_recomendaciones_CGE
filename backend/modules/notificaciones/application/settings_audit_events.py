from __future__ import annotations

from uuid import uuid4

from backend.core.audit.repository import record_audit
from backend.modules.usuarios.models import Usuario


def audit_notification_settings_change(
    *,
    request_id,
    actor: Usuario,
    previous: dict,
    current: dict,
    action: str = "UPDATE_NOTIFICATION_SETTINGS",
) -> None:
    """Registra un cambio de configuración o preferencias de notificación.

    Nunca se incluyen secretos SMTP ni credenciales en `detalles_json`.
    """
    record_audit(
        request_id=request_id or uuid4(),
        user=actor,
        action=action,
        entity="configuracion_notificacion",
        entity_id=None,
        details={"previous": previous, "current": current},
        modulo="notificaciones",
        ip_address=None,
    )
