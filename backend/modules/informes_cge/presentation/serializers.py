from django.urls import reverse
from rest_framework import serializers

from backend.modules.recomendaciones.models import InformeCGE


class InformeCreateSerializer(serializers.Serializer):
    numero_informe = serializers.CharField(max_length=100)
    periodo_auditado = serializers.CharField(max_length=100)
    fecha_notificacion = serializers.DateField()
    pdf_informe_url = serializers.URLField(required=False, allow_blank=True, default="")
    pdf_informe = serializers.FileField(
        required=False,
        help_text="Documento oficial en PDF (multipart/form-data). Alternativa a pdf_informe_url.",
    )

    def validate_pdf_informe(self, archivo):
        if not archivo.name.lower().endswith(".pdf") or archivo.content_type != "application/pdf":
            raise serializers.ValidationError("El documento oficial debe ser un archivo PDF.")
        signature = archivo.read(5)
        archivo.seek(0)
        if not signature.startswith(b"%PDF-"):
            raise serializers.ValidationError("El contenido no corresponde a un documento PDF.")
        return archivo

    def validate(self, attrs):
        if not attrs.get("pdf_informe_url") and not attrs.get("pdf_informe"):
            raise serializers.ValidationError("Adjunte el PDF oficial o proporcione su URL.")
        return attrs


class InformeSerializer(serializers.ModelSerializer):
    pdf_informe_url = serializers.SerializerMethodField()

    class Meta:
        model = InformeCGE
        fields = ["id", "numero_informe", "periodo_auditado", "fecha_notificacion", "pdf_informe_url", "creado_en"]

    def get_pdf_informe_url(self, informe) -> str:
        """URL externa registrada o, si se adjuntó el PDF, el endpoint autenticado que lo entrega."""
        if informe.pdf_informe:
            return reverse("informe-documento", args=[informe.id])
        return informe.pdf_informe_url


class PaginacionQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=25)
