"""Caso de uso: emitir dictamen UAI sobre una evidencia (RF-009, RF-010).

Reglas de negocio:
- Solo el rol UAI puede emitir dictámenes.
- La recomendación debe estar En Validación.
- La evidencia debe pertenecer a la recomendación, estar vigente y no tener dictamen.
- Solo una evidencia FINAL puede aprobarse.
- Aprobado → CUMPLIDA (requiere historial de revisión interna y evidencia validada).
- Rechazado → En Proceso (conserva archivos y revisiones previas).
- Operación atómica con select_for_update (bloqueo pesimista).
- Se audita dentro de la misma transacción.
"""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    ConflictError,
    NotFoundError,
    RecommendationState,
    ValidationError,
)
from backend.modules.recomendaciones.domain.state_machine import transition_state
from backend.modules.recomendaciones.models import DictamenUAI, Evidencia, Recomendacion
from backend.modules.usuarios.models import Usuario


class IssueDictamen:
    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        recommendation_id: UUID,
        evidence_id: UUID,
        approved: bool,
        observations: str = "",
        ip_address: str | None = None,
    ) -> DictamenUAI:
        # Bloqueo pesimista sobre la recomendación
        rec = (
            Recomendacion.objects.select_for_update()
            .filter(pk=recommendation_id)
            .first()
        )
        if rec is None:
            raise NotFoundError("La recomendación no existe.")

        # Validación de estado
        if rec.estado != Recomendacion.Estado.EN_VALIDACION:
            raise ConflictError(
                f"La recomendación en estado '{rec.estado}' no está lista para dictamen."
            )

        # La evidencia debe pertenecer a la recomendación
        evidence = (
            Evidencia.objects.select_for_update()
            .filter(pk=evidence_id, recomendacion=rec)
            .first()
        )
        if evidence is None:
            raise ValidationError("La evidencia no pertenece a la recomendación.")
        if evidence.estado != Evidencia.Estado.VIGENTE:
            raise ConflictError("No se puede dictaminar una evidencia anulada.")
        # Cada evidencia recibe un solo dictamen: una evidencia rechazada no puede
        # aprobarse después para cerrar la recomendación sin una entrega nueva.
        if DictamenUAI.objects.filter(evidencia=evidence).exists():
            raise ConflictError("La evidencia ya tiene un dictamen registrado.")
        # Un borrador es un avance, no una entrega: solo una evidencia FINAL
        # puede sustentar el cumplimiento.
        if approved and evidence.tipo != Evidencia.Tipo.FINAL:
            raise ConflictError("Solo una evidencia FINAL puede aprobarse como cumplimiento.")

        previous_state = rec.estado

        if approved:
            # Validar condición de CUMPLIDA: evidencia aprobada
            evidence.validada = True
            evidence.save(update_fields=["validada"])
            rec.estado = transition_state(
                rec.estado,
                RecommendationState.CUMPLIDA,
                had_internal_review=True,
                has_validated_evidence=True,
            )
        else:
            # Rechazo: conserva evidencia y registra observaciones
            rec.estado = transition_state(rec.estado, RecommendationState.EN_PROCESO)

        dictamen = DictamenUAI.objects.create(
            recomendacion=rec,
            evidencia=evidence,
            evaluador=actor,
            resultado=(
                DictamenUAI.Resultado.APROBADO
                if approved
                else DictamenUAI.Resultado.RECHAZADO
            ),
            observaciones_oficiales=observations,
        )
        rec.save(update_fields=["estado"])

        record_audit(
            request_id=request_id,
            user=actor,
            action="ISSUE_DICTAMEN",
            entity="recomendacion",
            entity_id=rec.id,
            previous_state=previous_state,
            new_state=rec.estado,
            details={
                "dictamen_id": str(dictamen.id),
                "approved": approved,
                "evidence_id": str(evidence_id),
            },
            ip_address=ip_address,
            modulo="evidencias",
        )
        return dictamen
