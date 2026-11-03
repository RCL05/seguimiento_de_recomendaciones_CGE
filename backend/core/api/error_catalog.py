from .response_envelope import build_envelope
from ..shared.domain_types import DomainError


def error_response(error: DomainError, request_id=None) -> tuple[dict, int]:
    return (
        build_envelope(
            success=False,
            message=str(error),
            errors={"code": error.code, "detail": str(error)},
            request_id=request_id,
        ),
        error.status_code,
    )

class ErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    FORBIDDEN = "PERMISSION_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    NOT_FOUND = "RESOURCE_NOT_FOUND"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    CONFLICT = "CONFLICT"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
