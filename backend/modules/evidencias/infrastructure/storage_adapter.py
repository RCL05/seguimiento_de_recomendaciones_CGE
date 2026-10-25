from __future__ import annotations

from pathlib import Path
from uuid import UUID

from django.conf import settings


class LocalEvidenceStorage:
    def save(self, evidence_id: UUID, filename: str, content: bytes) -> tuple[str, str]:
        directory = Path(settings.MEDIA_ROOT) / "evidencias"
        directory.mkdir(parents=True, exist_ok=True)
        ext = Path(filename).suffix.lower() or ".pdf"
        if ext != ".pdf":
            ext = ".pdf"
        target = directory / f"{evidence_id}{ext}"
        target.write_bytes(content)
        import hashlib

        sha256 = hashlib.sha256(content).hexdigest()
        return f"/media/evidencias/{evidence_id}{ext}", sha256


class InMemoryEvidenceStorage(LocalEvidenceStorage):
    def __init__(self):
        self.objects = {}

    def save(self, evidence_id: UUID, filename: str, content: bytes) -> tuple[str, str]:
        import hashlib

        self.objects[evidence_id] = content
        sha256 = hashlib.sha256(content).hexdigest()
        return f"memory://evidencias/{evidence_id}.pdf", sha256
