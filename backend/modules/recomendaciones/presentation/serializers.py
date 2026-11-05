from rest_framework import serializers

from backend.modules.recomendaciones.infrastructure.repositories import RecommendationRepository
from backend.modules.recomendaciones.models import DictamenUAI, Evidencia, PlanAccion, Recomendacion

PRIORIDADES = ["ALTA", "MEDIA", "BAJA"]


class RecomendacionCreateSerializer(serializers.Serializer):
    report_id = serializers.UUIDField(help_text="Informe CGE del que proviene la recomendación.")
    number = serializers.CharField(max_length=50)
    description = serializers.CharField()
    unit_id = serializers.CharField(max_length=50, help_text="Código de la unidad ejecutora.")
    legal_days = serializers.IntegerField(min_value=1, help_text="Plazo legal en días.")
    due_date = serializers.DateField(help_text="Fecha de vencimiento legal (America/Guayaquil).")
    priority = serializers.ChoiceField(choices=PRIORIDADES, default="MEDIA")


class RecomendacionQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=25)
    state = serializers.ChoiceField(choices=Recomendacion.Estado.choices, required=False)
    unit_id = serializers.CharField(required=False)
    priority = serializers.ChoiceField(choices=PRIORIDADES, required=False)
    due_date = serializers.DateField(required=False)
    due_before = serializers.DateField(required=False)
    due_after = serializers.DateField(required=False)
    vencida = serializers.BooleanField(
        required=False,
        allow_null=True,
        default=None,
        help_text="true: solo vencidas; false: solo dentro de plazo.",
    )


class RecomendacionSerializer(serializers.ModelSerializer):
    report_id = serializers.UUIDField(source="informe_id")
    number = serializers.CharField(source="numero_recomendacion")
    description = serializers.CharField(source="descripcion")
    unit_id = serializers.CharField(source="unidad_responsable.codigo")
    legal_days = serializers.IntegerField(source="plazo_legal_dias")
    due_date = serializers.DateField(source="fecha_vencimiento_legal")
    priority = serializers.CharField(source="prioridad")
    state = serializers.ChoiceField(source="estado", choices=Recomendacion.Estado.choices)
    vencida = serializers.SerializerMethodField(
        help_text="Plazo legal vencido sin cumplimiento. Es un indicador, no un estado del flujo."
    )
    overdue_registered_at = serializers.DateTimeField(source="vencimiento_registrado_en", allow_null=True)

    class Meta:
        model = Recomendacion
        fields = [
            "id",
            "report_id",
            "number",
            "description",
            "unit_id",
            "legal_days",
            "due_date",
            "priority",
            "state",
            "vencida",
            "overdue_registered_at",
        ]

    def get_vencida(self, recommendation) -> bool:
        annotated = getattr(recommendation, "vencida", None)
        if annotated is not None:
            return bool(annotated)
        return RecommendationRepository.esta_vencida(recommendation.pk)


class EvidenciaSerializer(serializers.ModelSerializer):
    recommendation_id = serializers.UUIDField(source="recomendacion_id")
    filename = serializers.CharField(source="nombre_archivo")
    size_bytes = serializers.IntegerField(source="tamano_bytes")
    sha256 = serializers.CharField(source="hash_sha256")
    uploaded_at = serializers.DateTimeField(source="fecha_carga")
    uploaded_by = serializers.UUIDField(source="subido_por_id")
    validated = serializers.BooleanField(source="validada")
    type = serializers.ChoiceField(source="tipo", choices=Evidencia.Tipo.choices)
    status = serializers.ChoiceField(source="estado", choices=Evidencia.Estado.choices)

    class Meta:
        model = Evidencia
        fields = [
            "id",
            "recommendation_id",
            "filename",
            "mime_type",
            "size_bytes",
            "sha256",
            "uploaded_at",
            "uploaded_by",
            "validated",
            "type",
            "status",
        ]


class RecomendacionDetalleSerializer(RecomendacionSerializer):
    evidencias = EvidenciaSerializer(many=True)

    class Meta(RecomendacionSerializer.Meta):
        fields = RecomendacionSerializer.Meta.fields + ["evidencias"]


class ReaperturaSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(
        choices=[Recomendacion.Estado.REABIERTA],
        help_text="Único cambio de estado manual admitido: CUMPLIDA → REABIERTA.",
    )
    motivo = serializers.CharField(max_length=1000, help_text="Hallazgo o razón de la reapertura.")


class HitoCreateSerializer(serializers.Serializer):
    descripcion_hito = serializers.CharField()
    fecha_compromiso = serializers.DateField(help_text="No puede exceder el plazo legal (RF-007).")


class HitoSerializer(serializers.ModelSerializer):
    recommendation_id = serializers.UUIDField(source="recomendacion_id")
    created_by = serializers.UUIDField(source="creado_por_id")

    class Meta:
        model = PlanAccion
        fields = ["id", "recommendation_id", "descripcion_hito", "fecha_compromiso", "completado", "created_by"]


class DictamenCreateSerializer(serializers.Serializer):
    evidence_id = serializers.UUIDField()
    approved = serializers.BooleanField()
    observaciones = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        # RF-010: un rechazo DEBE registrar observaciones para el ejecutor.
        if not attrs["approved"] and not attrs["observaciones"].strip():
            raise serializers.ValidationError(
                {"observaciones": "Las observaciones son obligatorias al rechazar una evidencia."}
            )
        return attrs


class DictamenSerializer(serializers.ModelSerializer):
    evidence_id = serializers.UUIDField(source="evidencia_id")
    evaluator_id = serializers.UUIDField(source="evaluador_id")
    observaciones = serializers.CharField(source="observaciones_oficiales")
    recomendacion = RecomendacionSerializer()

    class Meta:
        model = DictamenUAI
        fields = ["id", "resultado", "evidence_id", "evaluator_id", "observaciones", "fecha_dictamen", "recomendacion"]
