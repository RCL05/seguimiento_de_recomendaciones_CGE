"""Caso de uso para anular lógicamente una evidencia con auditoría obligatoria.

Reglas:
- Solo la UAI anula evidencias; el archivo y su hash se conservan.
- No se anula la evidencia aprobada de una recomendación Cumplida: dejaría el
  cumplimiento sin respaldo. Primero debe reabrirse la recomendación (RF-023).
- Si la recomendación está En Validación y ya no queda ninguna evidencia vigente
  pendiente de dictamen, vuelve a En Proceso para que el ejecutor cargue otra.
"""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    ConflictError,
    NotFoundError,
    PermissionDenied,
    RecommendationState,
)
from backend.modules.recomendaciones.domain.state_machine import transition_state
from backend.modules.recomendaciones.models import DictamenUAI, Evidencia, Recomendacion
from backend.modules.usuarios.models import Usuario


class AnularEvidencia:
    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        evidence_id: UUID,
        reason: str = "",
        ip_address: str | None = None,
    ) -> Evidencia:
        if actor.rol != Usuario.Rol.UAI:
            raise PermissionDenied("Solo UAI puede anular evidencias.")

        evidence = Evidencia.objects.filter(pk=evidence_id).only("recomendacion_id").first()
        if evidence is None:
            raise NotFoundError("La evidencia no existe.")
        # Mismo orden de bloqueo que el dictamen: primero la recomendación.
        rec = Recomendacion.objects.select_for_update().get(pk=evidence.recomendacion_id)
        evidence = Evidencia.objects.select_for_update().get(pk=evidence_id)
        if evidence.estado == Evidencia.Estado.ANULADA:
            raise ConflictError("La evidencia ya está anulada.")
        if rec.estado == Recomendacion.Estado.CUMPLIDA and evidence.validada:
            raise ConflictError(
                "La evidencia sustenta una recomendación cumplida; reabra la recomendación antes de anularla."
            )

        previous_state = evidence.estado
        evidence.estado = Evidencia.Estado.ANULADA
        evidence.save(update_fields=["estado"])
        record_audit(
            request_id=request_id,
            user=actor,
            action="ANULAR_EVIDENCIA",
            entity="evidencia",
            entity_id=evidence.id,
            previous_state=previous_state,
            new_state=evidence.estado,
            details={
                "recomendacion_id": str(evidence.recomendacion_id),
                "nombre_archivo": evidence.nombre_archivo,
                "hash_sha256": evidence.hash_sha256,
                "motivo": reason,
            },
            ip_address=ip_address,
            modulo="evidencias",
        )

        if rec.estado == Recomendacion.Estado.EN_VALIDACION and not self._has_pending_evidence(rec):
            previous_rec_state = rec.estado
            rec.estado = transition_state(rec.estado, RecommendationState.EN_PROCESO)
            rec.save(update_fields=["estado"])
            record_audit(
                request_id=request_id,
                user=actor,
                action="DEVOLVER_A_PROCESO",
                entity="recomendacion",
                entity_id=rec.id,
                previous_state=previous_rec_state,
                new_state=rec.estado,
                details={"motivo": "Se anuló la última evidencia pendiente de dictamen.", "evidencia_id": str(evidence.id)},
                ip_address=ip_address,
                modulo="evidencias",
            )
        return evidence

    @staticmethod
    def _has_pending_evidence(rec: Recomendacion) -> bool:
        dictaminated = DictamenUAI.objects.filter(recomendacion=rec, evidencia__isnull=False).values("evidencia_id")
        return (
            Evidencia.objects.filter(recomendacion=rec, estado=Evidencia.Estado.VIGENTE)
            .exclude(pk__in=dictaminated)
            .exists()
        )
