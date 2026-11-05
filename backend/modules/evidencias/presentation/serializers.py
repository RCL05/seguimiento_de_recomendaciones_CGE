from rest_framework import serializers

from backend.modules.recomendaciones.models import Evidencia


class AnulacionEvidenciaSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(
        choices=[Evidencia.Estado.ANULADA],
        help_text="Único cambio admitido: anulación lógica (la evidencia nunca se elimina).",
    )
    motivo = serializers.CharField(max_length=500)


class ArchivoQuerySerializer(serializers.Serializer):
    disposition = serializers.ChoiceField(choices=["inline", "attachment"], default="inline")


class IntegridadSerializer(serializers.Serializer):
    evidence_id = serializers.UUIDField()
    integra = serializers.BooleanField(help_text="true si el SHA-256 del archivo coincide con el registrado.")
    hash_registrado = serializers.CharField()
    hash_calculado = serializers.CharField()
