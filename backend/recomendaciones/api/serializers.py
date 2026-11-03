from rest_framework import serializers

from ..models import Asignacion, Evidencia, Recomendacion, Responsable, Unidad


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = ["id", "nombre", "siglas", "activa"]


class ResponsableSerializer(serializers.ModelSerializer):
    unidad_nombre = serializers.CharField(source="unidad.__str__", read_only=True)

    class Meta:
        model = Responsable
        fields = ["id", "nombre", "cargo", "email", "unidad", "unidad_nombre", "activo"]


class AsignacionSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.CharField(source="responsable.nombre", read_only=True)
    unidad_nombre = serializers.CharField(source="responsable.unidad.__str__", read_only=True)

    class Meta:
        model = Asignacion
        fields = [
            "id",
            "responsable",
            "responsable_nombre",
            "unidad_nombre",
            "es_principal",
            "asignado_en",
        ]


class EvidenciaSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    archivo_url = serializers.SerializerMethodField()
    recomendacion_codigo = serializers.CharField(source="recomendacion.codigo", read_only=True)

    class Meta:
        model = Evidencia
        fields = [
            "id",
            "recomendacion",
            "recomendacion_codigo",
            "archivo",
            "archivo_url",
            "tipo",
            "tipo_display",
            "estado",
            "estado_display",
            "descripcion",
            "mime",
            "tamano",
            "hash_archivo",
            "cargado_por",
            "motivo_anulacion",
            "anulada_en",
            "creado_en",
        ]
        read_only_fields = [
            "mime",
            "tamano",
            "hash_archivo",
            "estado",
            "motivo_anulacion",
            "anulada_en",
            "creado_en",
            "cargado_por",
        ]

    def get_archivo_url(self, obj):
        if not obj.archivo:
            return None
        request = self.context.get("request")
        url = obj.archivo.url
        return request.build_absolute_uri(url) if request else url


class RecomendacionSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    prioridad_display = serializers.CharField(source="get_prioridad_display", read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    asignaciones = AsignacionSerializer(many=True, read_only=True)
    evidencias_count = serializers.IntegerField(source="evidencias.count", read_only=True)
    responsables = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Responsable.objects.all(), required=False, write_only=True
    )

    class Meta:
        model = Recomendacion
        fields = [
            "id",
            "codigo",
            "descripcion",
            "origen",
            "prioridad",
            "prioridad_display",
            "estado",
            "estado_display",
            "fecha_emision",
            "fecha_limite",
            "esta_vencida",
            "asignaciones",
            "evidencias_count",
            "responsables",
            "creado_en",
            "actualizado_en",
        ]


class AnularEvidenciaSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=False, allow_blank=True, max_length=500)
