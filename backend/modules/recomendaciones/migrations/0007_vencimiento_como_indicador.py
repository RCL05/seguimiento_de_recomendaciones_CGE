"""Vencimiento como indicador (opción 2): se elimina el estado VENCIDA.

Cada recomendación en VENCIDA vuelve al estado de cumplimiento que tenía antes de
vencer, tomado del último evento MARK_OVERDUE de la bitácora. Si no existe, se usa
EN_PROCESO cuando ya tiene hitos y PENDIENTE en caso contrario. La fecha de ese
evento se conserva en `vencimiento_registrado_en` para no repetir la notificación.
"""
from django.db import migrations, models

ESTADOS_PREVIOS_VALIDOS = {"PENDIENTE", "EN_PROCESO", "EN_VALIDACION", "REABIERTA"}


def restaurar_estado_real(apps, schema_editor):
    Recomendacion = apps.get_model("recomendaciones", "Recomendacion")
    PlanAccion = apps.get_model("recomendaciones", "PlanAccion")
    AuditLog = apps.get_model("audit", "AuditLog")

    for rec in Recomendacion.objects.filter(estado="VENCIDA"):
        evento = (
            AuditLog.objects.filter(entidad_id=rec.id, accion="MARK_OVERDUE")
            .order_by("-timestamp_utc", "-id")
            .first()
        )
        if evento and evento.estado_anterior in ESTADOS_PREVIOS_VALIDOS:
            rec.estado = evento.estado_anterior
        elif PlanAccion.objects.filter(recomendacion_id=rec.id).exists():
            rec.estado = "EN_PROCESO"
        else:
            rec.estado = "PENDIENTE"
        if evento:
            rec.vencimiento_registrado_en = evento.timestamp_utc
        rec.save(update_fields=["estado", "vencimiento_registrado_en"])


class Migration(migrations.Migration):
    dependencies = [
        ("recomendaciones", "0006_informecge_pdf_informe_and_more"),
        ("audit", "0003_alter_auditlog_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="recomendacion",
            name="vencimiento_registrado_en",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(restaurar_estado_real, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="recomendacion",
            name="estado",
            field=models.CharField(
                choices=[
                    ("PENDIENTE", "Pendiente"),
                    ("EN_PROCESO", "En Proceso"),
                    ("EN_VALIDACION", "En Validación"),
                    ("REABIERTA", "Reabierta"),
                    ("CUMPLIDA", "Cumplida"),
                ],
                default="PENDIENTE",
                max_length=30,
            ),
        ),
    ]
