from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
