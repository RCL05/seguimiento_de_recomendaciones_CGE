from rest_framework import serializers


class UnidadEnMoraSerializer(serializers.Serializer):
    unidad_codigo = serializers.CharField()
    unidad_nombre = serializers.CharField()
    vencidas = serializers.IntegerField()
    total = serializers.IntegerField()


class TableroSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    cumplimiento_porcentaje = serializers.FloatField()
    semaforo_riesgo = serializers.ChoiceField(choices=["VERDE", "AMARILLO", "ROJO"])
    en_mora = serializers.IntegerField(help_text="Recomendaciones en estado VENCIDA.")
    en_revision_interna = serializers.IntegerField(help_text="Recomendaciones en estado EN_VALIDACION.")
    por_estado = serializers.DictField(child=serializers.IntegerField())
    unidades_en_mora = UnidadEnMoraSerializer(many=True)
    fecha_corte = serializers.DateField()


class AuditoriaQuerySerializer(serializers.Serializer):
    entity = serializers.CharField(required=False)
    entity_id = serializers.UUIDField(required=False)
    limit = serializers.IntegerField(min_value=1, max_value=500, default=100)


class AuditLogSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    request_id = serializers.UUIDField()
    timestamp_utc = serializers.DateTimeField()
    usuario = serializers.EmailField(source="usuario.correo_institucional", allow_null=True, default=None)
    modulo = serializers.CharField()
    accion = serializers.CharField()
    entidad = serializers.CharField()
    entidad_id = serializers.UUIDField(allow_null=True)
    estado_anterior = serializers.CharField(allow_null=True)
    estado_nuevo = serializers.CharField(allow_null=True)
    resultado = serializers.CharField()
    ip_origen = serializers.IPAddressField(allow_null=True)
