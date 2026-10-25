from __future__ import annotations

from uuid import UUID

from backend.core.audit.repository import record_audit


def audit_evidencia_cargada(
    *,
    request_id: UUID,
    user,
    recomendacion,
    evidencia,
    detalles: dict | None = None,
):
    return record_audit(
        request_id=request_id,
        user=user,
        action="EVIDENCIA_CARGADA",
        entity="evidencia",
        entity_id=getattr(evidencia, "id", None),
        previous_state=None,
        new_state=None,
        details={
            "recomendacion_id": str(getattr(recomendacion, "id", "")),
            "hash_sha256": getattr(evidencia, "hash_sha256", None),
            "nombre_archivo": getattr(evidencia, "nombre_archivo", None),
            **(detalles or {}),
        },
        modulo="evidencias",
    )


def audit_plan_creado(
    *,
    request_id: UUID,
    user,
    recomendacion,
    plan,
    detalles: dict | None = None,
):
    return record_audit(
        request_id=request_id,
        user=user,
        action="PLAN_ACCION_CREADO",
        entity="recomendacion",
        entity_id=getattr(recomendacion, "id", None),
        previous_state=None,
        new_state=None,
        details={"plan_id": str(getattr(plan, "id", "")), **(detalles or {})},
        modulo="evidencias",
    )
