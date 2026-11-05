from rest_framework import serializers

from backend.modules.notificaciones.infrastructure.preferences_models import TipoAlerta


class NotificacionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField(source="tipo")
    status = serializers.CharField(source="estado")
    scheduled_at = serializers.DateTimeField(source="programada_en")
    attempts = serializers.IntegerField(source="intentos")
    recommendation_id = serializers.UUIDField(source="recomendacion_id", allow_null=True)


class PreferenciaSerializer(serializers.Serializer):
    id = serializers.UUIDField(allow_null=True)
    usuario_id = serializers.UUIDField()
    tipo_alerta = serializers.ChoiceField(choices=TipoAlerta.choices)
    notificar_interno = serializers.BooleanField()
    notificar_email = serializers.BooleanField()
    activo = serializers.BooleanField()
    actualizado_en = serializers.DateTimeField(allow_null=True)


class PreferenciasSerializer(serializers.Serializer):
    usuario_id = serializers.UUIDField()
    preferencias = PreferenciaSerializer(many=True)


class PreferenciasUpdateSerializer(serializers.Serializer):
    usuario_id = serializers.UUIDField(required=False, help_text="Solo DTI puede editar a otro usuario.")
    preferencias = serializers.ListField(
        child=serializers.DictField(),
        help_text="Elementos con tipo_alerta y los indicadores notificar_interno, notificar_email, activo.",
    )


class ConfiguracionSerializer(serializers.Serializer):
    umbral_dias = serializers.IntegerField()
    notificaciones_activas = serializers.BooleanField()
    canal_interno_activo = serializers.BooleanField()
    canal_email_activo = serializers.BooleanField()
    destinatarios_vencimiento = serializers.ListField(child=serializers.CharField())
    destinatarios_mora = serializers.ListField(child=serializers.CharField())
    actualizado_en = serializers.DateTimeField()


class ConfiguracionUpdateSerializer(serializers.Serializer):
    umbral_dias = serializers.IntegerField(required=False)
    notificaciones_activas = serializers.BooleanField(required=False)
    canal_interno_activo = serializers.BooleanField(required=False)
    canal_email_activo = serializers.BooleanField(required=False)
    destinatarios_vencimiento = serializers.ListField(child=serializers.CharField(), required=False)
    destinatarios_mora = serializers.ListField(child=serializers.CharField(), required=False)


class EjecucionPlazosSerializer(serializers.Serializer):
    alertas_vencimiento = serializers.DictField()
    mora = serializers.DictField()
