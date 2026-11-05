from django.http import JsonResponse

from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope


ERRORS = {
    404: ("RESOURCE_NOT_FOUND", "No se encontró el recurso solicitado."),
    405: ("METHOD_NOT_ALLOWED", "El método HTTP no está permitido para este recurso."),
    500: ("INTERNAL_ERROR", "Ocurrió un error interno."),
}


def api_error_response(request, status: int) -> JsonResponse:
    code, message = ERRORS[status]
    return JsonResponse(
        build_envelope(
            success=False,
            message=message,
            errors={"code": code, "detail": message},
            request_id=request_id_from(request),
        ),
        status=status,
    )


def handler404(request, exception):
    return api_error_response(request, 404)


def handler500(request):
    return api_error_response(request, 500)


class ApiErrorEnvelopeMiddleware:
    """Envuelve 404/405/500 generados fuera de DRF (rutas inexistentes, errores del framework)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        data = getattr(response, "data", None)
        if isinstance(data, dict) and "success" in data:
            # Ya viene con la envoltura universal desde DRF: conservar su mensaje específico.
            return response
        if response.status_code in ERRORS:
            normalized = api_error_response(request, response.status_code)
            # RFC 9110 §15.5.6: un 405 DEBE indicar los métodos admitidos en Allow.
            if response.has_header("Allow"):
                normalized["Allow"] = response["Allow"]
            return normalized
        return response
