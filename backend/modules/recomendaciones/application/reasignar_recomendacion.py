"""Caso de uso: reasignar una recomendación a otra unidad responsable (RF-003).

Reglas de negocio:
- Solo la UAI puede reasignar recomendaciones.
- La unidad destino debe existir y ser distinta de la unidad actual.
- El motivo es obligatorio para conservar la trazabilidad del cambio.
- Se conserva el historial: la unidad anterior y la nueva quedan en `AuditLog`,
  sin eliminar ni sobrescribir la bitácora previa.
- Operación atómica con select_for_update y auditada en la misma transacción.
"""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    NotFoundError,
    PermissionDenied,
    ValidationError,
)
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario


class ReasignarRecomendacion:
    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        recommendation_id: UUID,
        unit_id: str,
        reason: str,
        ip_address: str | None = None,
    ) -> Recomendacion:
        if actor.rol != Usuario.Rol.UAI:
            raise PermissionDenied("Solo el rol UAI puede reasignar recomendaciones.")
        if not reason or not reason.strip():
            raise ValidationError("El motivo de la reasignación es obligatorio.")
        if not unit_id or not unit_id.strip():
            raise ValidationError("La unidad destino es obligatoria.")

        rec = (
            Recomendacion.objects.select_for_update()
            .select_related("informe", "unidad_responsable")
            .filter(pk=recommendation_id)
            .first()
        )
        if rec is None:
            raise NotFoundError("La recomendación no existe.")

        target_unit = UnidadOrganica.objects.filter(codigo=unit_id.strip()).first()
        if target_unit is None:
            raise ValidationError(f"La unidad destino '{unit_id}' no existe.")
        if target_unit.id == rec.unidad_responsable_id:
            raise ValidationError("La recomendación ya está asignada a esa unidad.")

        previous_unit = rec.unidad_responsable
        rec.unidad_responsable = target_unit
        rec.save(update_fields=["unidad_responsable"])

        record_audit(
            request_id=request_id,
            user=actor,
            action="REASSIGN",
            entity="recomendacion",
            entity_id=rec.id,
            previous_state=rec.estado,
            new_state=rec.estado,
            details={
                "motivo": reason.strip(),
                "unidad_anterior": previous_unit.codigo,
                "unidad_anterior_id": str(previous_unit.id),
                "unidad_nueva": target_unit.codigo,
                "unidad_nueva_id": str(target_unit.id),
            },
            ip_address=ip_address,
            modulo="recomendaciones",
        )
        return rec
