import uuid

from django.db import models

from backend.modules.usuarios.models import Usuario


class AuditLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    request_id = models.UUIDField(default=uuid.uuid4)
    usuario = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.PROTECT)
    timestamp_utc = models.DateTimeField(auto_now_add=True)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    modulo = models.CharField(max_length=100)
    accion = models.CharField(max_length=100)
    entidad = models.CharField(max_length=100)
    entidad_id = models.UUIDField(null=True, blank=True)
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    detalles_json = models.JSONField(default=dict)

    class Meta:
        db_table = "audit_logs"
        ordering = ["timestamp_utc", "id"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise TypeError("Los registros de auditoría son inmutables.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Los registros de auditoría son inmutables.")
