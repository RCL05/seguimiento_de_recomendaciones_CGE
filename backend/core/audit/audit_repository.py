from __future__ import annotations

from backend.core.audit.models import AuditLog


class AuditRepository:
    @staticmethod
    def query_read_only(**filters):
        qs = AuditLog.objects.all().order_by("-timestamp_utc", "-id")
        if filters.get("entity"):
            qs = qs.filter(entidad=filters["entity"])
        if filters.get("entity_id"):
            qs = qs.filter(entidad_id=filters["entity_id"])
        if filters.get("user_id"):
            qs = qs.filter(usuario_id=filters["user_id"])
        return qs

    @staticmethod
    def forbid_modification():
        raise PermissionError("Los registros de auditoría son inmutables y no pueden modificarse ni eliminarse.")
