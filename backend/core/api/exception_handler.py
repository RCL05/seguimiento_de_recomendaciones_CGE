"""Manejador global de errores de DRF -> contrato universal y catálogo institucional.

Constitución, "Organización Centralizada de Errores": los códigos son estables
(`UPPER_SNAKE_CASE`) y los 500 nunca exponen trazas ni detalles técnicos.
"""
from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf
from rest_framework.response import Response

from .error_catalog import error_response
from .request_context import request_id_from
from .response_envelope import build_envelope
from ..shared.domain_types import DomainError

logger = logging.getLogger(__name__)

# (código institucional, mensaje por defecto en español)
_DRF_ERRORS: list[tuple[type[Exception], str, str]] = [
    (drf.NotAuthenticated, "AUTHENTICATION_REQUIRED", "Se requiere un token Bearer válido."),
    (drf.AuthenticationFailed, "AUTHENTICATION_REQUIRED", "El token de sesión no es válido."),
    (drf.PermissionDenied, "PERMISSION_DENIED", "No tiene permisos para realizar esta operación."),
    (drf.NotFound, "RESOURCE_NOT_FOUND", "No se encontró el recurso solicitado."),
    (drf.MethodNotAllowed, "METHOD_NOT_ALLOWED", "El método HTTP no está permitido para este recurso."),
    (drf.ParseError, "VALIDATION_ERROR", "El cuerpo debe ser JSON válido."),
    (drf.ValidationError, "VALIDATION_ERROR", "Los datos enviados no son válidos."),
    (drf.UnsupportedMediaType, "UNSUPPORTED_MEDIA_TYPE", "El tipo de contenido no es compatible."),
    (drf.NotAcceptable, "NOT_ACCEPTABLE", "No se puede producir el formato solicitado."),
    (drf.Throttled, "TOO_MANY_REQUESTS", "Se superó el límite de solicitudes."),
]


def _first_message(detail) -> str | None:
    """Primer mensaje legible de un `ValidationError.detail` anidado."""
    if isinstance(detail, dict):
        for field, value in detail.items():
            message = _first_message(value)
            if message:
                return message if field == "non_field_errors" else f"{field}: {message}"
    elif isinstance(detail, list):
        for value in detail:
            message = _first_message(value)
            if message:
                return message
    elif detail:
        return str(detail)
    return None


def _drf_payload(exception: drf.APIException) -> tuple[str, str, object | None]:
    for exception_type, code, default_message in _DRF_ERRORS:
        if isinstance(exception, exception_type):
            if isinstance(exception, drf.ValidationError):
                fields = exception.detail
                return code, _first_message(fields) or default_message, fields
            if isinstance(exception, drf.ParseError):
                return code, default_message, None
            detail = exception.detail
            custom = str(detail) if isinstance(detail, str) and detail != exception.default_detail else None
            return code, custom or default_message, None
    return "HTTP_ERROR", str(exception.detail), None


def handle_exception(exception, context=None):
    request = context.get("request") if context else None
    request_id = request_id_from(request) if request is not None else None

    if isinstance(exception, DomainError):
        payload, status = error_response(exception, request_id)
        response = Response(payload, status=status)
        if status == 401:
            # RFC 9110 §11.6.1: toda respuesta 401 indica cómo autenticarse.
            response["WWW-Authenticate"] = 'Bearer realm="sitra-cge"'
        return response

    if isinstance(exception, Http404):
        exception = drf.NotFound()
    elif isinstance(exception, DjangoPermissionDenied):
        exception = drf.PermissionDenied()

    if isinstance(exception, drf.APIException):
        code, message, fields = _drf_payload(exception)
        errors = {"code": code, "detail": message}
        if fields is not None:
            errors["fields"] = fields
        response = Response(
            build_envelope(success=False, message=message, errors=errors, request_id=request_id),
            status=exception.status_code,
        )
        auth_header = getattr(exception, "auth_header", None)
        if auth_header:
            response["WWW-Authenticate"] = auth_header
        wait = getattr(exception, "wait", None)
        if wait:
            response["Retry-After"] = str(int(wait))
        return response

    logger.exception("Error no controlado (request_id=%s)", request_id)
    message = "Ocurrió un error interno."
    return Response(
        build_envelope(
            success=False,
            message=message,
            errors={"code": "INTERNAL_ERROR", "detail": message},
            request_id=request_id,
        ),
        status=500,
    )
