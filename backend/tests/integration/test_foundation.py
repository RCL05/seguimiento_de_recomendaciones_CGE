import pytest

from backend.core.api.error_catalog import ErrorCodes, error_response
from backend.core.api.response_envelope import build_envelope
from backend.core.auth.authorization import require_role, require_same_unit
from backend.core.shared.domain_types import (
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDenied,
    Role,
    User,
    ValidationError,
)

pytestmark = pytest.mark.django_db


def test_envelope_exitoso_y_de_error_comparten_estructura():
    success = build_envelope(success=True, message="ok", data={"id": "1"})
    assert set(success) == {"success", "message", "data", "errors", "meta"}
    assert success["success"] is True
    assert success["errors"] is None
    assert success["meta"]["version"] == "v1"
    assert success["meta"]["request_id"]

    payload, status = error_response(ValidationError("Dato inválido"))
    assert status == 400
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["errors"]["code"] == ErrorCodes.VALIDATION_ERROR
    assert payload["errors"]["detail"] == "Dato inválido"
    assert "request_id" in payload["meta"]


@pytest.mark.parametrize(
    ("error", "status", "code"),
    [
        (ValidationError("x"), 400, ErrorCodes.VALIDATION_ERROR),
        (PermissionDenied("x"), 403, ErrorCodes.PERMISSION_DENIED),
        (NotFoundError("x"), 404, ErrorCodes.RESOURCE_NOT_FOUND),
        (ConflictError("x"), 409, ErrorCodes.CONFLICT),
        (DomainError("x"), 409, ErrorCodes.BUSINESS_RULE_VIOLATION),
    ],
)
def test_catalogo_de_errores_mapea_estado_y_codigo(error, status, code):
    payload, payload_status = error_response(error)
    assert payload_status == status
    assert payload["errors"]["code"] == code


def test_autorizacion_por_rol_y_unidad():
    executor_a = User(id="exec-a", role=Role.EJECUTOR, unit_id="unit-a")
    executor_b = User(id="exec-b", role=Role.EJECUTOR, unit_id="unit-b")
    uai = User(id="uai", role=Role.UAI, unit_id="unit-a")

    require_role(uai, Role.UAI)
    require_same_unit(executor_a, "unit-a")

    with pytest.raises(PermissionDenied):
        require_role(executor_a, Role.UAI)

    with pytest.raises(PermissionDenied):
        require_same_unit(executor_b, "unit-a")

    with pytest.raises(PermissionDenied):
        require_same_unit(uai, "unit-a")
