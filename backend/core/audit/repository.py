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
    resultado: str = "OK",
    modulo: str = "api",
) -> AuditLog:
    """Crea un registro de auditoría inmutable.

    Sólo se puede crear (INSERT); nunca UPDATE ni DELETE.
    """
    return AuditLog.objects.create(
        request_id=request_id,
        usuario=user,
        ip_origen=ip_address,
        modulo=modulo,
        accion=action,
        entidad=entity,
        entidad_id=entity_id,
        estado_anterior=previous_state,
        estado_nuevo=new_state,
        resultado=resultado,
        detalles_json=details or {},
    )


def query_audit_log(
    *,
    entity: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    limit: int = 100,
):
    """Consulta de solo lectura del log de auditoría.

    Disponible para roles UAI y CGE_AUDITOR.
    Devuelve un QuerySet ordenado de más reciente a más antiguo.
    """
    qs = AuditLog.objects.select_related("usuario").order_by("-timestamp_utc", "-id")
    if entity:
        qs = qs.filter(entidad=entity)
    if entity_id:
        qs = qs.filter(entidad_id=entity_id)
    if user_id:
        qs = qs.filter(usuario_id=user_id)
    return qs[:limit]
