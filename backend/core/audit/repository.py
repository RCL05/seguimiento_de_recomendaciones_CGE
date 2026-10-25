from uuid import UUID

from backend.core.audit.models import AuditLog
from backend.modules.usuarios.models import Usuario


def record_audit(
    *,
    request_id: UUID,
    user: Usuario | None,
    action: str,
    entity: str,
    entity_id: UUID | None,
    previous_state: str | None = None,
    new_state: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    return AuditLog.objects.create(
        request_id=request_id,
        usuario=user,
        ip_origen=ip_address,
        modulo="api",
        accion=action,
        entidad=entity,
        entidad_id=entity_id,
        estado_anterior=previous_state,
        estado_nuevo=new_state,
        detalles_json=details or {},
    )
