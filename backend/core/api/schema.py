"""Piezas reutilizables para documentar el contrato OpenAPI con drf-spectacular."""
from __future__ import annotations

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers


class PaginationSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class MetaSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()
    pagination = PaginationSerializer(allow_null=True)


class ErrorDetailSerializer(serializers.Serializer):
    code = serializers.ChoiceField(
        choices=[
            "VALIDATION_ERROR",
            "AUTHENTICATION_REQUIRED",
            "PERMISSION_DENIED",
            "RESOURCE_NOT_FOUND",
            "METHOD_NOT_ALLOWED",
            "BUSINESS_RULE_VIOLATION",
            "CONFLICT",
            "PAYLOAD_TOO_LARGE",
            "UNSUPPORTED_MEDIA_TYPE",
            "INTERNAL_ERROR",
        ]
    )
    detail = serializers.CharField()
    fields = serializers.DictField(required=False, help_text="Errores por campo (solo VALIDATION_ERROR).")


class ErrorEnvelopeSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()
    data = serializers.JSONField(allow_null=True, default=None)
    errors = ErrorDetailSerializer()
    meta = MetaSerializer()


def envelope(name: str, data_serializer=None, *, many: bool = False):
    """Esquema `SuccessEnvelope` cuyo `data` es `data_serializer`."""
    data_field = (
        data_serializer(many=many) if data_serializer is not None else serializers.JSONField(allow_null=True)
    )
    return inline_serializer(
        name=f"{name}Envelope",
        fields={
            "success": serializers.BooleanField(default=True),
            "message": serializers.CharField(),
            "data": data_field,
            "errors": serializers.JSONField(allow_null=True, default=None),
            "meta": MetaSerializer(),
        },
    )


_ERROR_DESCRIPTIONS = {
    400: "VALIDATION_ERROR: campos, formatos o tipos inválidos.",
    401: "AUTHENTICATION_REQUIRED: token Bearer ausente, inválido o expirado.",
    403: "PERMISSION_DENIED: el rol no puede ejecutar la operación.",
    404: "RESOURCE_NOT_FOUND: inexistente o no visible para el usuario (BOLA/IDOR).",
    405: "METHOD_NOT_ALLOWED: ver la cabecera Allow.",
    409: "CONFLICT / BUSINESS_RULE_VIOLATION: transición o regla de negocio incumplida.",
    413: "PAYLOAD_TOO_LARGE: el PDF supera el tamaño máximo.",
    500: "INTERNAL_ERROR: error inesperado procesando la solicitud.",
}


def errors(*statuses: int) -> dict[int, OpenApiResponse]:
    """Respuestas de error documentadas con la envoltura universal."""
    statuses = tuple(dict.fromkeys((*statuses, 500)))
    return {
        status: OpenApiResponse(
            ErrorEnvelopeSerializer,
            description=_ERROR_DESCRIPTIONS[status],
            examples=[OpenApiExample(
                "Error de servidor",
                value={"success": False, "message": "Error interno del servidor", "data": None,
                       "errors": {"code": "INTERNAL_ERROR", "detail": "No fue posible procesar la solicitud."},
                       "meta": {"request_id": "4a54c2a9-8b76-4a9f-a1f3-7bf8a8a2f001",
                                "timestamp": "2026-11-05T12:00:00Z", "version": "1.0.0", "pagination": None}},
                response_only=True,
                status_codes=[str(status)],
            )] if status == 500 else None,
        )
        for status in statuses
    }


class JWTBearerScheme(OpenApiAuthenticationExtension):
    target_class = "backend.core.auth.authentication.JWTBearerAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT emitido por POST /api/v1/auth/login-sso (expira en 1 hora).",
        }
