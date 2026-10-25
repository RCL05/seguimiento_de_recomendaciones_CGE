from rest_framework.response import Response
from .error_catalog import error_response
from .request_context import request_id_from
from ..shared.domain_types import DomainError


def handle_exception(exception, context=None):
    request = context.get("request") if context else None
    if isinstance(exception, DomainError):
        payload, status = error_response(exception, request_id_from(request) if request else None)
        return Response(payload, status=status)
    payload, status = error_response(
        DomainError("Ocurrió un error interno."),
        request_id_from(request) if request else None,
    )
    payload["errors"]["code"] = "INTERNAL_ERROR"
    return Response(payload, status=500)
