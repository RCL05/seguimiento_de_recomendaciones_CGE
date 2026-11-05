"""Caso de uso: reabrir una recomendación cumplida (CUMPLIDA -> REABIERTA).

Reglas de negocio:
- Solo la UAI puede reabrir, con un motivo obligatorio (p. ej., hallazgo posterior).
- La transición pasa por la máquina de estados del dominio.
- El ejecutor reanuda después con un nuevo hito (REABIERTA -> EN_PROCESO).
- Operación atómica con select_for_update y auditada en la misma transacción.
"""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    NotFoundError,
    PermissionDenied,
    RecommendationState,
    ValidationError,
)
from backend.modules.recomendaciones.domain.state_machine import transition_state
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario


class ReabrirRecomendacion:
    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        recommendation_id: UUID,
        reason: str,
        ip_address: str | None = None,
    ) -> Recomendacion:
        if actor.rol != Usuario.Rol.UAI:
            raise PermissionDenied("Solo el rol UAI puede reabrir recomendaciones.")
        if not reason or not reason.strip():
            raise ValidationError("El motivo de la reapertura es obligatorio.")

        rec = (
            Recomendacion.objects.select_for_update()
            .select_related("informe", "unidad_responsable")
            .filter(pk=recommendation_id)
            .first()
        )
        if rec is None:
            raise NotFoundError("La recomendación no existe.")

        previous_state = rec.estado
        rec.estado = transition_state(rec.estado, RecommendationState.REABIERTA)
        # Nuevo ciclo de cumplimiento: si vuelve a vencer, se notificará otra vez.
        rec.vencimiento_registrado_en = None
        rec.save(update_fields=["estado", "vencimiento_registrado_en"])

        record_audit(
            request_id=request_id,
            user=actor,
            action="REOPEN",
            entity="recomendacion",
            entity_id=rec.id,
            previous_state=previous_state,
            new_state=rec.estado,
            details={"motivo": reason.strip()},
            ip_address=ip_address,
            modulo="recomendaciones",
        )
        return rec
