"""Verificación de salud del servicio (pública, sin autenticación)."""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny

from backend.core.api.base import ApiView, ok
from backend.core.api.schema import envelope


class SaludSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ok"])


class HealthView(ApiView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Operación"],
        operation_id="verificarSalud",
        summary="Comprobar que el servicio está disponible",
        auth=[],
        responses={200: envelope("Salud", SaludSerializer)},
    )
    def get(self, request):
        return ok(request, {"status": "ok"}, "Servicio disponible")
