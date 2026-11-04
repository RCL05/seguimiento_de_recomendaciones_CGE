import hashlib
from pathlib import Path
from typing import Iterable
from uuid import UUID

from django.conf import settings

from backend.core.shared.domain_types import PayloadTooLarge


class EvidenceStorage:
    chunk_size = 64 * 1024

    @property
    def directory(self) -> Path:
        return Path(settings.MEDIA_ROOT) / "evidencias"

    def save_stream(
        self,
        evidence_id: UUID,
        chunks: Iterable[bytes],
        *,
        max_size: int,
    ) -> tuple[str, str, int, bytes]:
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory / f"{evidence_id}.pdf"
        digest = hashlib.sha256()
        total_size = 0
        signature = bytearray()

        try:
            with target.open("wb") as destination:
                for chunk in chunks:
                    if not chunk:
                        continue
                    total_size += len(chunk)
                    if total_size > max_size:
                        raise PayloadTooLarge("El PDF supera el tamaño máximo permitido.")
                    if len(signature) < 5:
                        signature.extend(chunk[: 5 - len(signature)])
                    digest.update(chunk)
                    destination.write(chunk)
        except Exception:
            target.unlink(missing_ok=True)
            raise

        return (
            f"/media/evidencias/{evidence_id}.pdf",
            digest.hexdigest(),
            total_size,
            bytes(signature),
        )

    def delete(self, evidence_id: UUID) -> None:
        target = self.directory / f"{evidence_id}.pdf"
        target.unlink(missing_ok=True)
