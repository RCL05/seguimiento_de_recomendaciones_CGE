"""Caso de uso: cargar evidencia PDF (RF-008).

Reglas de negocio:
- Solo el ejecutor de la unidad responsable puede subir evidencia.
- La recomendación debe estar en EN_EJECUCION o RECHAZADA_CORRECCION.
- El archivo debe ser PDF válido, ≤ 30 MB, con contenido que coincida con su extensión.
- Se calcula SHA-256 y se almacena el archivo detrás del puerto de almacenamiento.
- La recomendación transiciona a EN_REVISION_INTERNA.
- Operación atómica con select_for_update.
- Se audita dentro de la misma transacción.
"""
from __future__ import annotations

from uuid import UUID, uuid4

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.files.pdf_integrity import validate_pdf
from backend.core.shared.domain_types import ConflictError, NotFoundError
from backend.modules.recomendaciones.infrastructure.storage import EvidenceStorage
from backend.modules.recomendaciones.models import Evidencia, Recomendacion
from backend.modules.usuarios.models import Usuario

MAX_SIZE_BYTES = 30 * 1024 * 1024  # 30 MB


class UploadEvidencia:
    def __init__(self, storage: EvidenceStorage | None = None) -> None:
        self._storage = storage or EvidenceStorage()

    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        recommendation_id: UUID,
        filename: str,
        content: bytes,
        ip_address: str | None = None,
    ) -> Evidencia:
        # Bloqueo pesimista
        rec = (
            Recomendacion.objects.select_for_update()
            .select_related("unidad_responsable")
            .filter(pk=recommendation_id)
            .first()
        )
        if rec is None:
            raise NotFoundError("La recomendación no existe.")

        # Autorización a nivel de objeto
        if actor.unidad_org_id != rec.unidad_responsable_id:
            record_audit(
                request_id=request_id,
                user=actor,
                action="ACCESS_DENIED",
                entity="recomendacion",
                entity_id=rec.id,
                details={"reason": "different_unit"},
                resultado="DENIED",
                ip_address=ip_address,
                modulo="evidencias",
            )
            raise NotFoundError("La recomendación no existe.")

        # Validación de estado
        if rec.estado not in {
            Recomendacion.Estado.EN_EJECUCION,
            Recomendacion.Estado.RECHAZADA_CORRECCION,
        }:
            raise ConflictError(
                f"La recomendación en estado '{rec.estado}' no acepta evidencias."
            )

        # Validación PDF (extensión, MIME, contenido, tamaño)
        digest = validate_pdf(filename, content)

        # Persistencia del archivo
        evidence_id = uuid4()
        storage_url, _ = self._storage.save(evidence_id, filename, content)

        evidence = Evidencia.objects.create(
            id=evidence_id,
            recomendacion=rec,
            nombre_archivo=filename,
            mime_type="application/pdf",
            tamano_bytes=len(content),
            url_almacenamiento=storage_url,
            hash_sha256=digest,
            subido_por=actor,
            validada=False,
        )

        previous_state = rec.estado
        rec.estado = Recomendacion.Estado.EN_REVISION_INTERNA
        rec.save(update_fields=["estado"])

        record_audit(
            request_id=request_id,
            user=actor,
            action="UPLOAD_EVIDENCE",
            entity="recomendacion",
            entity_id=rec.id,
            previous_state=previous_state,
            new_state=rec.estado,
            details={"evidence_id": str(evidence.id), "sha256": digest, "size": len(content)},
            ip_address=ip_address,
            modulo="evidencias",
        )
        return evidence
