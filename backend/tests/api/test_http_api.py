import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, str(Path(__file__).parents[2]))

django = pytest.importorskip("django")
django.setup()

from django.test import Client

from backend.core.api.views import reports, service


@pytest.fixture(autouse=True)
def reset_service():
    service.recommendations.clear()
    service.evidences.clear()
    service.plans.clear()
    reports.clear()


def test_health_and_dashboard_are_available():
    client = Client()
    assert client.get("/health/").json()["data"]["status"] == "ok"
    assert "SITRA-CGE UNL" in client.get("/").content.decode()


def test_recommendation_flow_returns_universal_envelope():
    client = Client()
    payload = {
        "number": "R-001",
        "description": "Implementar control institucional",
        "unit_id": "unit-a",
        "legal_days": 30,
        "due_date": "2026-12-31",
    }
    created = client.post(
        "/api/v1/recomendaciones",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert created.status_code == 201
    body = created.json()
    assert body["success"] is True
    recommendation_id = body["data"]["id"]

    listed = client.get("/api/v1/recomendaciones")
    assert listed.status_code == 200
    assert listed.json()["data"][0]["id"] == recommendation_id


def test_invalid_login_has_structured_error():
    response = Client().post(
        "/api/v1/auth/login-sso",
        data="{}",
        content_type="application/json",
    )
    assert response.status_code == 409
    assert response.json()["errors"]["code"] == "BUSINESS_RULE_VIOLATION"


def test_report_and_plan_routes_are_available():
    client = Client()
    report = client.post(
        "/api/v1/informes",
        data=json.dumps(
            {
                "numero_informe": "INF-001",
                "periodo_auditado": "2025",
                "fecha_notificacion": "2026-01-10",
                "pdf_informe_url": "https://example.test/inf-001.pdf",
            }
        ),
        content_type="application/json",
    )
    assert report.status_code == 201

    recommendation = client.post(
        "/api/v1/recomendaciones",
        data=json.dumps(
            {
                "number": "R-002",
                "description": "Actualizar controles",
                "unit_id": "unit-a",
                "legal_days": 30,
                "due_date": "2026-12-31",
            }
        ),
        content_type="application/json",
    )
    recommendation_id = recommendation.json()["data"]["id"]
    plan = client.post(
        f"/api/v1/recomendaciones/{recommendation_id}/plan-accion",
        data=json.dumps(
            {
                "descripcion_hito": "Presentar plan",
                "fecha_compromiso": "2026-11-01",
            }
        ),
        content_type="application/json",
        HTTP_X_ROLE="EJECUTOR",
        HTTP_X_UNIT_ID="unit-a",
    )
    assert plan.status_code == 201
    assert plan.json()["data"]["recommendation_id"] == recommendation_id
