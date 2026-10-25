import hashlib
from pathlib import Path
from uuid import UUID

from django.conf import settings


class EvidenceStorage:
    def save(self, evidence_id: UUID, filename: str, content: bytes) -> tuple[str, str]:
        directory = Path(settings.MEDIA_ROOT) / "evidence"
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f"{evidence_id}.pdf"
        target.write_bytes(content)
        return f"/media/evidence/{evidence_id}.pdf", hashlib.sha256(content).hexdigest()
