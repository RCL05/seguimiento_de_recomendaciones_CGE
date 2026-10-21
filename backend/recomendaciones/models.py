import hashlib

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .validators import RutaEvidenciaPDF, validar_archivo_pdf


class EstadoRecomendacion(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    EN_PROCESO = "EN_PROCESO", "En Proceso"
    EN_VALIDACION = "EN_VALIDACION", "En Validación"
    CUMPLIDA = "CUMPLIDA", "Cumplida"
    VENCIDA = "VENCIDA", "Vencida"
    REABIERTA = "REABIERTA", "Reabierta"


class Prioridad(models.TextChoices):
    ALTA = "ALTA", "Alta"
    MEDIA = "MEDIA", "Media"
    BAJA = "BAJA", "Baja"


class Unidad(models.Model):
    nombre = models.CharField("Nombre", max_length=200, unique=True)
    siglas = models.CharField("Siglas", max_length=20, blank=True)
    activa = models.BooleanField("Activa", default=True)

    class Meta:
        verbose_name = "Unidad Administrativa"
        verbose_name_plural = "Unidades Administrativas"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.siglas} - {self.nombre}" if self.siglas else self.nombre


class Responsable(models.Model):
    nombre = models.CharField("Nombre", max_length=200)
    cargo = models.CharField("Cargo", max_length=150, blank=True)
    email = models.EmailField("Correo electrónico", blank=True)
    unidad = models.ForeignKey(
        Unidad,
        on_delete=models.PROTECT,
        related_name="responsables",
        verbose_name="Unidad",
    )
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Recomendacion(models.Model):
    codigo = models.CharField("Código", max_length=50, unique=True)
    descripcion = models.TextField("Descripción")
    origen = models.CharField("Origen", max_length=200, blank=True, default="CGE")
    prioridad = models.CharField(
        "Prioridad",
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=EstadoRecomendacion.choices,
        default=EstadoRecomendacion.PENDIENTE,
    )
    fecha_emision = models.DateField("Fecha de emisión", default=timezone.localdate)
    fecha_limite = models.DateField("Fecha límite")
    responsables = models.ManyToManyField(
        Responsable,
        through="Asignacion",
        related_name="recomendaciones",
        verbose_name="Responsables",
    )
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)
    actualizado_en = models.DateTimeField("Actualizado en", auto_now=True)

    class Meta:
        verbose_name = "Recomendación"
        verbose_name_plural = "Recomendaciones"
        ordering = ["fecha_limite", "codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.get_estado_display()}"

    def clean(self):
        if self.fecha_limite and self.fecha_emision and self.fecha_limite < self.fecha_emision:
            raise ValidationError(
                {"fecha_limite": "La fecha límite no puede ser anterior a la fecha de emisión."}
            )

    @property
    def esta_vencida(self):
        if self.estado in (EstadoRecomendacion.CUMPLIDA, EstadoRecomendacion.VENCIDA):
            return self.estado == EstadoRecomendacion.VENCIDA
        return bool(self.fecha_limite and self.fecha_limite < timezone.localdate())


class Asignacion(models.Model):
    recomendacion = models.ForeignKey(
        Recomendacion,
        on_delete=models.CASCADE,
        related_name="asignaciones",
        verbose_name="Recomendación",
    )
    responsable = models.ForeignKey(
        Responsable,
        on_delete=models.PROTECT,
        related_name="asignaciones",
        verbose_name="Responsable",
    )
    es_principal = models.BooleanField("Es responsable principal", default=False)
    asignado_en = models.DateTimeField("Asignado en", auto_now_add=True)

    class Meta:
        verbose_name = "Asignación de Responsable"
        verbose_name_plural = "Asignaciones de Responsables"
        constraints = [
            models.UniqueConstraint(
                fields=["recomendacion", "responsable"],
                name="unique_recomendacion_responsable",
            )
        ]
        ordering = ["-es_principal", "responsable__nombre"]

    def __str__(self):
        return f"{self.recomendacion.codigo} → {self.responsable.nombre}"


class TipoEvidencia(models.TextChoices):
    BORRADOR = "BORRADOR", "Borrador de avance"
    FINAL = "FINAL", "Entrega final"


class EstadoEvidencia(models.TextChoices):
    VIGENTE = "VIGENTE", "Vigente"
    ANULADA = "ANULADA", "Anulada"


class Evidencia(models.Model):
    recomendacion = models.ForeignKey(
        Recomendacion,
        on_delete=models.PROTECT,
        related_name="evidencias",
        verbose_name="Recomendación",
    )
    archivo = models.FileField(
        "Archivo PDF",
        upload_to=RutaEvidenciaPDF(),
        validators=[validar_archivo_pdf],
    )
    tipo = models.CharField(
        "Tipo",
        max_length=10,
        choices=TipoEvidencia.choices,
        default=TipoEvidencia.BORRADOR,
    )
    estado = models.CharField(
        "Estado",
        max_length=10,
        choices=EstadoEvidencia.choices,
        default=EstadoEvidencia.VIGENTE,
    )
    descripcion = models.CharField("Descripción", max_length=250, blank=True)
    mime = models.CharField("MIME", max_length=100, blank=True)
    tamano = models.PositiveIntegerField("Tamaño (bytes)", default=0)
    hash_archivo = models.CharField("Hash SHA-256", max_length=64, blank=True, editable=False)

    cargado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evidencias_cargadas",
        verbose_name="Cargado por",
    )
    motivo_anulacion = models.TextField("Motivo de anulación", blank=True)
    anulada_en = models.DateTimeField("Anulada en", null=True, blank=True)
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        verbose_name = "Evidencia"
        verbose_name_plural = "Evidencias"
        ordering = ["-creado_en"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(tamano__gte=0),
                name="evidencia_tamano_no_negativo",
            )
        ]

    def __str__(self):
        return f"{self.recomendacion.codigo} - {self.get_tipo_display()} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        if self.archivo and not self.tamano:
            self.tamano = self.archivo.size
        if self.archivo and not self.hash_archivo:
            self.hash_archivo = self.calcular_hash()
        if not self.mime:
            self.mime = "application/pdf"
        super().save(*args, **kwargs)

    def calcular_hash(self):
        digest = hashlib.sha256()
        self.archivo.seek(0)
        for bloque in self.archivo.chunks():
            digest.update(bloque)
        self.archivo.seek(0)
        return digest.hexdigest()

    @property
    def esta_anulada(self):
        return self.estado == EstadoEvidencia.ANULADA

    def anular(self, motivo=""):
        if self.esta_anulada:
            raise ValidationError("La evidencia ya está anulada.")
        self.estado = EstadoEvidencia.ANULADA
        self.motivo_anulacion = motivo
        self.anulada_en = timezone.now()
        self.save(update_fields=["estado", "motivo_anulacion", "anulada_en"])

