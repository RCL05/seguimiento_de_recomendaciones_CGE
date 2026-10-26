import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models

import backend.modules.notificaciones.infrastructure.preferences_models


class Migration(migrations.Migration):

    dependencies = [
        ("notificaciones", "0001_initial"),
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificacion",
            name="canal_interno",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="notificacion",
            name="canal_email",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="notificacion",
            name="leida",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="PreferenciaNotificacion",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "tipo_alerta",
                    models.CharField(
                        choices=[
                            ("ALERTA_VENCIMIENTO", "Alerta de vencimiento"),
                            ("EN_MORA", "Recomendación en mora"),
                        ],
                        max_length=50,
                    ),
                ),
                ("notificar_interno", models.BooleanField(default=True)),
                ("notificar_email", models.BooleanField(default=True)),
                ("activo", models.BooleanField(default=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="preferencias_notificacion",
                        to="usuarios.usuario",
                    ),
                ),
            ],
            options={
                "db_table": "preferencias_notificacion",
                "ordering": ["usuario_id", "tipo_alerta"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("usuario", "tipo_alerta"),
                        name="uq_preferencia_usuario_tipo",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="ConfiguracionNotificacion",
            fields=[
                (
                    "id",
                    models.PositiveSmallIntegerField(
                        default=1, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "umbral_dias",
                    models.PositiveSmallIntegerField(
                        default=15,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(90),
                        ],
                    ),
                ),
                ("notificaciones_activas", models.BooleanField(default=True)),
                ("canal_interno_activo", models.BooleanField(default=True)),
                ("canal_email_activo", models.BooleanField(default=True)),
                (
                    "destinatarios_vencimiento",
                    models.JSONField(blank=True, default=list),
                ),
                (
                    "destinatarios_mora",
                    models.JSONField(blank=True, default=list),
                ),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "actualizado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="configuraciones_notificacion",
                        to="usuarios.usuario",
                    ),
                ),
            ],
            options={
                "db_table": "configuracion_notificaciones",
            },
        ),
    ]
