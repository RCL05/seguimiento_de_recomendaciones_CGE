from __future__ import annotations

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from backend.modules.usuarios.models import Usuario


class TipoAlerta(models.TextChoices):
    ALERTA_VENCIMIENTO = "ALERTA_VENCIMIENTO", "Alerta de vencimiento"
    EN_MORA = "EN_MORA", "Recomendación en mora"


class PreferenciaNotificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="preferencias_notificacion",
    )
    tipo_alerta = models.CharField(max_length=50, choices=TipoAlerta.choices)
    notificar_interno = models.BooleanField(default=True)
    notificar_email = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "preferencias_notificacion"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "tipo_alerta"],
                name="uq_preferencia_usuario_tipo",
            ),
        ]
        ordering = ["usuario_id", "tipo_alerta"]


class ConfiguracionNotificacion(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    umbral_dias = models.PositiveSmallIntegerField(
        default=15,
        validators=[MinValueValidator(1), MaxValueValidator(90)],
    )
    notificaciones_activas = models.BooleanField(default=True)
    canal_interno_activo = models.BooleanField(default=True)
    canal_email_activo = models.BooleanField(default=True)
    destinatarios_vencimiento = models.JSONField(default=list, blank=True)
    destinatarios_mora = models.JSONField(default=list, blank=True)
    actualizado_por = models.ForeignKey(
        Usuario,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="configuraciones_notificacion",
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "configuracion_notificaciones"

    @classmethod
    def load(cls) -> "ConfiguracionNotificacion":
        config, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "destinatarios_vencimiento": ["UAI"],
                "destinatarios_mora": ["UAI", "RECTORADO"],
            },
        )
        return config

    def snapshot(self) -> dict:
        return {
            "umbral_dias": self.umbral_dias,
            "notificaciones_activas": self.notificaciones_activas,
            "canal_interno_activo": self.canal_interno_activo,
            "canal_email_activo": self.canal_email_activo,
            "destinatarios_vencimiento": list(self.destinatarios_vencimiento or []),
            "destinatarios_mora": list(self.destinatarios_mora or []),
        }
