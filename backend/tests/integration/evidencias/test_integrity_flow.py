import hashlib
import uuid
from types import SimpleNamespace

from backend.modules.evidencias.application.verify_integrity import verify_evidence_integrity

ORIGINAL_PDF = b"%PDF-1.7\ncontenido original\n%%EOF\n"
MODIFIED_PDF = b"%PDF-1.7\ncontenido alterado\n%%EOF\n"


def _evidence_for(content: bytes):
    return SimpleNamespace(
        id=uuid.uuid4(),
        hash_sha256=hashlib.sha256(content).hexdigest(),
    )


def test_hash_original_coincide_y_evidencia_alterada_se_detecta():
    evidence = _evidence_for(ORIGINAL_PDF)

    intact = verify_evidence_integrity(evidence=evidence, storage_content=ORIGINAL_PDF)
    assert intact["ok"] is True
    assert intact["computed_hash"] == evidence.hash_sha256

    tampered = verify_evidence_integrity(evidence=evidence, storage_content=MODIFIED_PDF)
    assert tampered["ok"] is False
    assert tampered["stored_hash"] == evidence.hash_sha256
    assert tampered["computed_hash"] != evidence.hash_sha256


def test_contenido_vacio_o_hash_ausente_no_se_considera_integro():
    evidence = _evidence_for(ORIGINAL_PDF)
    assert verify_evidence_integrity(evidence=evidence, storage_content=b"")["ok"] is False

    without_hash = SimpleNamespace(id=uuid.uuid4(), hash_sha256="")
    assert verify_evidence_integrity(evidence=without_hash, storage_content=ORIGINAL_PDF)["ok"] is False
