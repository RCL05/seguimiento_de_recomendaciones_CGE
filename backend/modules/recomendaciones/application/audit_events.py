from __future__ import annotations

from uuid import UUID

from backend.core.audit.repository import record_audit


def audit_recomendacion_creada(
    *,
    request_id: UUID,
    user,
    recomendacion,
    detalles: dict | None = None,
):
    return record_audit(
        request_id=request_id,
        user=user,
        action="RECOMENDACION_CREADA",
        entity="recomendacion",
        entity_id=getattr(recomendacion, "id", None),
        previous_state=None,
        new_state=getattr(recomendacion, "estado", None) or getattr(recomendacion, "state", None),
        details=detalles or {},
        modulo="recomendaciones",
    )


def audit_informe_creado(
    *,
    request_id: UUID,
    user,
    informe,
    detalles: dict | None = None,
):
    return record_audit(
        request_id=request_id,
        user=user,
        action="INFORME_CGE_CREADO",
        entity="informe_cge",
        entity_id=getattr(informe, "id", None),
        previous_state=None,
        new_state=None,
        details=detalles or {},
        modulo="informes_cge",
    )
