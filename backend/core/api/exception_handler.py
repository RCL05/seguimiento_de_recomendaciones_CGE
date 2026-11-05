from rest_framework.response import Response

from .error_catalog import error_response
from .request_context import request_id_from
from .response_envelope import build_envelope
from ..shared.domain_types import DomainError


def handle_exception(exception, context=None):
    request = context.get("request") if context else None
    request_id = request_id_from(request) if request else None
    if isinstance(exception, DomainError):
        payload, status = error_response(exception, request_id)
        return Response(payload, status=status)

    status = getattr(exception, "status_code", 500)
    if not isinstance(status, int) or not 400 <= status <= 599:
        status = 500
    if status >= 500:
        message = "Ocurrio un error interno."
        code = "INTERNAL_ERROR"
    else:
        message = str(getattr(exception, "detail", "La solicitud no pudo completarse."))
        code = str(getattr(exception, "default_code", "HTTP_ERROR"))

    return Response(
        build_envelope(
            success=False,
            message=message,
            errors={"code": code, "detail": message},
            request_id=request_id,
        ),
        status=status,
    )
