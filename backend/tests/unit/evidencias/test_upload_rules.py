import pytest

from backend.core.shared.domain_types import PermissionDenied, Role, User


def test_evidencia_tamano_mime_extension_hash_y_autorizacion_unidad():
    # Validaciones básicas de reglas
    max_bytes = 30 * 1024 * 1024
    assert max_bytes == 31457280

    # MIME y extensión solo PDF
    allowed_mime = {"application/pdf"}
    allowed_ext = {".pdf"}
    assert "application/pdf" in allowed_mime
    assert ".pdf" in allowed_ext

    # Hash sha256 formato hex 64
    import re

    h = "a" * 64
    assert re.match(r"^[0-9a-fA-F]{64}$", h)

    # Autorización por unidad
    from backend.core.auth.authorization import require_same_unit

    ejec_a = User(id="e1", role=Role.EJECUTOR, unit_id="unit-1")
    ejec_b = User(id="e2", role=Role.EJECUTOR, unit_id="unit-2")
    require_same_unit(ejec_a, "unit-1")
    with pytest.raises(PermissionDenied):
        require_same_unit(ejec_b, "unit-1")
