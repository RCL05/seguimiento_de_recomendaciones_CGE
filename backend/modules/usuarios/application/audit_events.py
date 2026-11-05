from __future__ import annotations

from uuid import UUID

from backend.core.audit.repository import record_audit


def audit_auth_event(*, request_id: UUID, user=None, action: str, details: dict | None = None):
    return record_audit(
        request_id=request_id,
        user=user,
        action=action,
        entity="usuario",
        entity_id=getattr(user, "id", None),
        details=details or {},
        modulo="usuarios",
    )
