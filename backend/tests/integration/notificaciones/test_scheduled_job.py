"""Job programado `evaluar_plazos`: composición del resultado y ejecución real (RF-011, RF-012, RF-021)."""

import json
from io import StringIO

import pytest
from django.core.management import call_command

from backend.core.audit.models import AuditLog
from backend.modules.notificaciones.infrastructure import scheduled_jobs
from backend.modules.notificaciones.models import Notificacion
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario
from tests import factories


def _stub_jobs(monkeypatch, alerts, overdue):
    monkeypatch.setattr(scheduled_jobs, "send_deadline_alerts", lambda: alerts)
    monkeypatch.setattr(
        scheduled_jobs, "mark_overdue_recommendations", lambda: overdue
    )


def test_run_scheduled_evaluations_compone_resultados(monkeypatch):
    alerts = {"scheduled": 2, "skipped": 1, "delivered": 2}
    overdue = {"marked": 1, "skipped": 0, "delivered": 1}
    _stub_jobs(monkeypatch, alerts, overdue)

    result = scheduled_jobs.run_scheduled_evaluations()

    assert result["alertas_vencimiento"] == alerts
    assert result["mora"] == overdue
    assert result["status"] == "ok"
    assert result["evaluated_at"].endswith("+00:00")


def test_comando_evaluar_plazos_emite_json(monkeypatch):
    _stub_jobs(
        monkeypatch,
        {"scheduled": 0, "skipped": 0, "delivered": 0},
        {"marked": 0, "skipped": 0, "delivered": 0},
    )
    output = StringIO()

    call_command("evaluar_plazos", stdout=output)

    payload = json.loads(output.getvalue())
    assert payload["status"] == "ok"
    assert payload["alertas_vencimiento"]["scheduled"] == 0
    assert payload["mora"]["marked"] == 0


# Ejecución real del comando, sin sustituir la lógica de alertas ni de mora.


def _ejecutar_comando():
    output = StringIO()
    call_command("evaluar_plazos", stdout=output)
    return json.loads(output.getvalue())


@pytest.mark.django_db
def test_comando_real_alerta_registra_mora_y_es_idempotente():
    factories.usuario(Usuario.Rol.EJECUTOR, "ejecutor-job", "DEP-A")
    factories.usuario(Usuario.Rol.RECTORADO, "rectorado-job")
    proxima = factories.recomendacion(dias_para_vencer=5)
    vencida = factories.recomendacion(dias_para_vencer=-2)
    lejana = factories.recomendacion(dias_para_vencer=40)

    primera = _ejecutar_comando()

    assert primera["status"] == "ok"
    assert primera["alertas_vencimiento"]["scheduled"] >= 2  # ejecutor y UAI
    assert primera["mora"]["marked"] == 1
    assert Notificacion.objects.filter(recomendacion=proxima, tipo="ALERTA_VENCIMIENTO").exists()
    assert Notificacion.objects.filter(recomendacion=vencida, tipo="EN_MORA").exists()
    assert not Notificacion.objects.filter(recomendacion=lejana).exists()
    vencida.refresh_from_db()
    assert vencida.vencimiento_registrado_en is not None
    assert vencida.estado == Recomendacion.Estado.EN_PROCESO  # el vencimiento no es un estado
    total = Notificacion.objects.count()

    segunda = _ejecutar_comando()

    assert segunda["alertas_vencimiento"]["scheduled"] == 0
    assert segunda["mora"]["marked"] == 0
    assert Notificacion.objects.count() == total
    assert AuditLog.objects.filter(accion="MARK_OVERDUE", entidad_id=vencida.id).count() == 1
