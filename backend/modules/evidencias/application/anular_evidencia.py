"""Caso de uso para anular lógicamente una evidencia con auditoría obligatoria."""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import ConflictError, NotFoundError, PermissionDenied
from backend.modules.recomendaciones.models import Evidencia
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

        evidence = (
            Evidencia.objects.select_for_update()
            .select_related("recomendacion")
            .filter(pk=evidence_id)
            .first()
        )
        if evidence is None:
            raise NotFoundError("La evidencia no existe.")
        if evidence.estado == Evidencia.Estado.ANULADA:
            raise ConflictError("La evidencia ya está anulada.")

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
        return evidence
