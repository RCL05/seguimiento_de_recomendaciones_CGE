from __future__ import annotations

import hashlib

from backend.core.audit.repository import record_audit


def verify_evidence_integrity(*, evidence, storage_content: bytes = None, request_id=None, user=None):
    stored_hash = getattr(evidence, "hash_sha256", "")
    content = storage_content or b""
    computed = hashlib.sha256(content).hexdigest()
    ok = stored_hash.lower() == computed.lower() if stored_hash else False
    try:
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
    except Exception:
        pass
    return {"ok": ok, "stored_hash": stored_hash, "computed_hash": computed}
