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
