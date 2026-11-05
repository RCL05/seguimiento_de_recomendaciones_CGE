from __future__ import annotations

from uuid import UUID

from backend.core.api.exception_handler import ErrorCodes
from backend.core.api.response_envelope import error_response
from backend.core.audit.repository import query_audit_log as _query_audit_log
from backend.core.auth.authorization import has_role
from backend.modules.usuarios.models import Role

AUDIT_LOG_ALLOWED_ROLES = {Role.UAI, Role.CGE_AUDITOR}


def query_audit_log(
    *,
    actor=None,
    entity: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    limit: int = 100,
):
    """Consulta de historial de auditoría con autorización.

    Solo permite acceso a usuarios con rol UAI o CGE_AUDITOR.
    Delegando la consulta al repositorio de auditoría (solo lectura).
    """

    if actor is None or not has_role(actor, *AUDIT_LOG_ALLOWED_ROLES):
        return error_response(
            code=ErrorCodes.FORBIDDEN,
            message="No tiene permisos para consultar la auditoría.",
            status=403,
        )

    logs = _query_audit_log(
        entity=entity,
        entity_id=entity_id,
        user_id=user_id,
        limit=limit,
    )
    return logs


def get_audit_history(
    *,
    actor=None,
    entity: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    limit: int = 100,
):
    """Alias semántico para la consulta de historial de auditoría."""

    return query_audit_log(
        actor=actor,
        entity=entity,
        entity_id=entity_id,
        user_id=user_id,
        limit=limit,
    )
