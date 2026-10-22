import uuid

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from backend.modules.usuarios.models import UnidadOrganica, Usuario


class InformeCGE(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_informe = models.CharField(max_length=100, unique=True)
    periodo_auditado = models.CharField(max_length=100)
    fecha_notificacion = models.DateField()
    pdf_informe_url = models.URLField()
    creado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "informes_cge"


class Recomendacion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_PLANIFICACION = "EN_PLANIFICACION", "En planificación"
        EN_EJECUCION = "EN_EJECUCION", "En ejecución"
        EN_REVISION_INTERNA = "EN_REVISION_INTERNA", "En revisión interna"
        CUMPLIDA = "CUMPLIDA", "Cumplida"
        RECHAZADA_CORRECCION = "RECHAZADA_CORRECCION", "Rechazada/corrección"
        EN_MORA = "EN_MORA", "En mora"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    informe = models.ForeignKey(InformeCGE, on_delete=models.PROTECT, related_name="recomendaciones")
    numero_recomendacion = models.CharField(max_length=50)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=30)
    unidad_responsable = models.ForeignKey(
        UnidadOrganica,
        on_delete=models.PROTECT,
        related_name="recomendaciones",
    )
    plazo_legal_dias = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    fecha_vencimiento_legal = models.DateField()
    estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.PENDIENTE)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recomendaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["informe", "numero_recomendacion"],
                name="uq_recomendacion_informe_numero",
            ),
        ]


class PlanAccion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.PROTECT, related_name="planes")
    descripcion_hito = models.TextField()
    fecha_compromiso = models.DateField()
    completado = models.BooleanField(default=False)
    creado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT)

    class Meta:
        db_table = "planes_accion"


class Evidencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.PROTECT, related_name="evidencias")
    plan_accion = models.ForeignKey(PlanAccion, null=True, blank=True, on_delete=models.PROTECT)
    nombre_archivo = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, default="application/pdf")
    tamano_bytes = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(30 * 1024 * 1024),
        ],
    )
    url_almacenamiento = models.URLField()
    hash_sha256 = models.CharField(
        max_length=64,
        validators=[RegexValidator(r"^[0-9a-fA-F]{64}$")],
    )
    fecha_carga = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    inmutable = models.BooleanField(default=True)
    validada = models.BooleanField(default=False)

    class Meta:
        db_table = "evidencias"


class DictamenUAI(models.Model):
    class Resultado(models.TextChoices):
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.PROTECT, related_name="dictamenes")
    evidencia = models.ForeignKey(Evidencia, null=True, blank=True, on_delete=models.PROTECT)
    evaluador = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    resultado = models.CharField(max_length=20, choices=Resultado.choices)
    observaciones_oficiales = models.TextField(blank=True)
    fecha_dictamen = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dictamenes_uai"
