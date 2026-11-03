"""Caso de uso: rechazo de evidencia con observaciones (RF-010)."""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import ConflictError, NotFoundError, ValidationError
from backend.modules.recomendaciones.models import DictamenUAI, Evidencia, Recomendacion
from backend.modules.usuarios.models import Usuario


class RejectEvidence:
    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        recommendation_id: UUID,
        evidence_id: UUID,
        observations: str,
        ip_address: str | None = None,
    ) -> DictamenUAI:
        rec = (
            Recomendacion.objects.select_for_update()
            .filter(pk=recommendation_id)
            .first()
        )
        if rec is None:
            raise NotFoundError("La recomendación no existe.")

        if rec.estado != Recomendacion.Estado.EN_REVISION_INTERNA:
            raise ConflictError(
                f"La recomendación en estado '{rec.estado}' no está lista para dictamen."
            )

        evidence = Evidencia.objects.filter(pk=evidence_id, recomendacion=rec).first()
        if evidence is None:
            raise ValidationError("La evidencia no pertenece a la recomendación.")

        previous_state = rec.estado
        rec.estado = Recomendacion.Estado.RECHAZADA_CORRECCION

        dictamen = DictamenUAI.objects.create(
            recomendacion=rec,
            evidencia=evidence,
            evaluador=actor,
            resultado=DictamenUAI.Resultado.RECHAZADO,
            observaciones_oficiales=observations or "",
        )
        rec.save(update_fields=["estado"])

        record_audit(
            request_id=request_id,
            user=actor,
            action="REJECT_EVIDENCE",
            entity="recomendacion",
            entity_id=rec.id,
            previous_state=previous_state,
            new_state=rec.estado,
            details={
                "dictamen_id": str(dictamen.id),
                "evidence_id": str(evidence_id),
                "observations": observations,
            },
            ip_address=ip_address,
            modulo="evidencias",
        )
        return dictamen
