import hashlib
from pathlib import Path

from ..shared.domain_types import ValidationError


def validate_pdf(filename: str, content: bytes, max_size: int = 30 * 1024 * 1024) -> str:
    if Path(filename).suffix.lower() != ".pdf":
        raise ValidationError("La evidencia debe tener extensión PDF.")
    if not content.startswith(b"%PDF-"):
        raise ValidationError("El contenido no corresponde a un documento PDF.")
    if len(content) == 0 or len(content) > max_size:
        raise ValidationError("El tamaño del PDF no es válido.")
    return hashlib.sha256(content).hexdigest()
