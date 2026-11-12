"""Application use case for receiving a PDF evidence stream."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
from uuid import UUID, uuid4

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    ConflictError,
    NotFoundError,
    PayloadTooLarge,
    RecommendationState,
    ValidationError,
)
from backend.modules.recomendaciones.domain.state_machine import transition_state
from backend.modules.recomendaciones.infrastructure.storage import EvidenceStorage
from backend.modules.recomendaciones.models import Evidencia, Recomendacion
from backend.modules.usuarios.models import Usuario

MAX_SIZE_BYTES = int(os.getenv("MAX_PDF_SIZE_BYTES", str(30 * 1024 * 1024)))


class UploadEvidencia:
    def __init__(self, storage: EvidenceStorage | None = None) -> None:
        self._storage = storage or EvidenceStorage()

    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        recommendation_id: UUID,
        filename: str,
        content: bytes | Iterable[bytes],
        evidence_type: str = Evidencia.Tipo.BORRADOR,
        ip_address: str | None = None,
    ) -> Evidencia:
        if Path(filename).suffix.lower() != ".pdf":
            raise ValidationError("La evidencia debe tener extension PDF.")
        if evidence_type not in Evidencia.Tipo.values:
            raise ValidationError("El tipo de evidencia debe ser BORRADOR o FINAL.")

        self._authorize(actor, recommendation_id, request_id, ip_address)
        chunks = (content,) if isinstance(content, bytes) else content
        evidence_id = uuid4()
        storage_url, digest, size, signature = self._storage.save_stream(
            evidence_id,
            chunks,
            max_size=MAX_SIZE_BYTES,
        )

        try:
            if not signature.startswith(b"%PDF-"):
                raise ValidationError("El contenido no corresponde a un documento PDF.")
            if size == 0:
                raise ValidationError("El PDF esta vacio.")

            with transaction.atomic():
                recommendation = (
                    Recomendacion.objects.select_for_update()
                    .select_related("unidad_responsable")
                    .filter(pk=recommendation_id)
                    .first()
                )
                if recommendation is None:
                    raise NotFoundError("La recomendacion no existe.")
                self._check_authorization(actor, recommendation, request_id, ip_address)
                self._check_state(recommendation)

                evidence = Evidencia.objects.create(
                    id=evidence_id,
                    recomendacion=recommendation,
                    nombre_archivo=filename,
                    mime_type="application/pdf",
                    tamano_bytes=size,
                    url_almacenamiento=storage_url,
                    hash_sha256=digest,
                    subido_por=actor,
                    tipo=evidence_type,
                    validada=False,
                )

                previous_state = recommendation.estado
                recommendation.estado = transition_state(
                    recommendation.estado,
                    RecommendationState.EN_VALIDACION,
                )
                recommendation.save(update_fields=["estado"])

                record_audit(
                    request_id=request_id,
                    user=actor,
                    action="UPLOAD_EVIDENCE",
                    entity="recomendacion",
                    entity_id=recommendation.id,
                    previous_state=previous_state,
                    new_state=recommendation.estado,
                    details={
                        "evidence_id": str(evidence.id),
                        "sha256": digest,
                        "size": size,
                    },
                    ip_address=ip_address,
                    modulo="evidencias",
                )
            return evidence
        except Exception:
            self._storage.delete(evidence_id)
            raise

    def _authorize(
        self,
        actor: Usuario,
        recommendation_id: UUID,
        request_id: UUID,
        ip_address: str | None,
    ) -> None:
        recommendation = (
            Recomendacion.objects.select_related("unidad_responsable")
            .filter(pk=recommendation_id)
            .first()
        )
        if recommendation is None:
            raise NotFoundError("La recomendacion no existe.")
        self._check_authorization(actor, recommendation, request_id, ip_address)
        self._check_state(recommendation)

    @staticmethod
    def _check_authorization(
        actor: Usuario,
        recommendation: Recomendacion,
        request_id: UUID,
        ip_address: str | None,
    ) -> None:
        if actor.unidad_org_id == recommendation.unidad_responsable_id:
            return
        record_audit(
            request_id=request_id,
            user=actor,
            action="ACCESS_DENIED",
            entity="recomendacion",
            entity_id=recommendation.id,
            details={"reason": "different_unit"},
            resultado="DENIED",
            ip_address=ip_address,
            modulo="evidencias",
        )
        raise NotFoundError("La recomendacion no existe.")

    @staticmethod
    def _check_state(recommendation: Recomendacion) -> None:
        # Sin plan o en otro estado es el mismo caso: la recomendación no admite evidencias
        # en su estado actual (409), aunque el mensaje indique qué falta.
        if recommendation.estado == Recomendacion.Estado.PENDIENTE:
            raise ConflictError(
                "Debe registrar primero el Plan de accion antes de cargar evidencias."
            )
        if recommendation.estado != Recomendacion.Estado.EN_PROCESO:
            raise ConflictError(
                f"La recomendacion en estado '{recommendation.estado}' no acepta evidencias."
            )
