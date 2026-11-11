"""Verificación de integridad de evidencias por SHA-256 (RNF-001, HU-5 escenario 2)."""
from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import UUID

from django.conf import settings

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import NotFoundError, PermissionDenied, Role
from backend.modules.recomendaciones.models import Evidencia
from backend.modules.usuarios.models import Usuario

ROLES_VERIFICACION = {Role.UAI.value, Role.CGE_AUDITOR.value}


def verify_evidence_integrity(*, evidence, storage_content: bytes = None, request_id=None, user=None):
    stored_hash = getattr(evidence, "hash_sha256", "")
    content = storage_content or b""
    computed = hashlib.sha256(content).hexdigest()
    ok = stored_hash.lower() == computed.lower() if stored_hash else False
    if request_id:
        record_audit(
            request_id=request_id,
            user=user,
            action="VERIFY_INTEGRITY",
            entity="evidencia",
            entity_id=getattr(evidence, "id", None),
            details={"ok": ok, "stored_hash": stored_hash, "computed_hash": computed},
            modulo="evidencias",
            resultado="OK" if ok else "FAIL",
        )
    return {"ok": ok, "stored_hash": stored_hash, "computed_hash": computed}


class VerificarIntegridadEvidencia:
    """Recalcula el SHA-256 del archivo almacenado y lo compara con el registrado."""

    def execute(self, *, actor: Usuario, evidence_id: UUID, request_id: UUID) -> dict:
        if actor.rol not in ROLES_VERIFICACION:
            raise PermissionDenied("Solo UAI o el auditor CGE pueden verificar la integridad.")
        evidence = Evidencia.objects.filter(pk=evidence_id).first()
        if evidence is None:
            raise NotFoundError("La evidencia no existe.")
        path = Path(settings.MEDIA_ROOT) / "evidencias" / f"{evidence.id}.pdf"
        if not path.is_file():
            raise NotFoundError("El archivo de evidencia no está disponible.")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(64 * 1024), b""):
                digest.update(chunk)
        computed = digest.hexdigest()
        ok = computed.lower() == evidence.hash_sha256.lower()
        record_audit(
            request_id=request_id,
            user=actor,
            action="VERIFY_INTEGRITY",
            entity="evidencia",
            entity_id=evidence.id,
            details={"ok": ok, "stored_hash": evidence.hash_sha256, "computed_hash": computed},
            modulo="evidencias",
            resultado="OK" if ok else "FAIL",
        )
        return {
            "evidence_id": evidence.id,
            "integra": ok,
            "hash_registrado": evidence.hash_sha256,
            "hash_calculado": computed,
        }
