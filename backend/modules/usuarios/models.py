import uuid

from django.db import models


class UnidadOrganica(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    padre = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="hijas",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "unidades_organicas"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Usuario(models.Model):
    class Rol(models.TextChoices):
        DTI = "DTI", "DTI"
        UAI = "UAI", "UAI"
        EJECUTOR = "EJECUTOR", "Ejecutor"
        RECTORADO = "RECTORADO", "Rectorado"
        CGE_AUDITOR = "CGE_AUDITOR", "Auditor CGE"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correo_institucional = models.EmailField(max_length=320, unique=True)
    nombres = models.CharField(max_length=200)
    rol = models.CharField(max_length=20, choices=Rol.choices)
    unidad_org = models.ForeignKey(
        UnidadOrganica,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="usuarios",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "usuarios"
        ordering = ["correo_institucional"]

    def __str__(self):
        return self.correo_institucional
