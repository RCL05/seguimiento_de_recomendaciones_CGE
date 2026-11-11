import json
from io import StringIO

from django.core.management import call_command

from backend.modules.notificaciones.infrastructure import scheduled_jobs


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
