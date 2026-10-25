import uuid

from django.db import models

from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario


class Notificacion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ENVIADA = "ENVIADA", "Enviada"
        FALLIDA = "FALLIDA", "Fallida"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recomendacion = models.ForeignKey(Recomendacion, null=True, blank=True, on_delete=models.PROTECT)
    destinatario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=50)
    clave_idempotencia = models.CharField(max_length=200, unique=True)
    programada_en = models.DateTimeField()
    enviada_en = models.DateTimeField(null=True, blank=True)
    intentos = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        db_table = "notificaciones"
