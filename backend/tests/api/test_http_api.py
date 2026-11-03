import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def _post(client, path, payload, role="UAI", user="uai-http", unit="UAI"):
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_X_ROLE=role,
        HTTP_X_USER_ID=user,
        HTTP_X_UNIT_ID=unit,
    )


def _create_report(client, number="INF-HTTP-001"):
    response = _post(
        client,
        "/api/v1/informes",
        {
            "numero_informe": number,
            "periodo_auditado": "2026",
            "fecha_notificacion": "2026-01-10",
            "pdf_informe_url": "https://example.test/informe.pdf",
        },
    )
    assert response.status_code == 201, response.content
    return response.json()["data"]["id"]


def test_health_and_dashboard_are_available():
    client = Client()
    assert client.get("/health/").json()["data"]["status"] == "ok"
    assert "SITRA-CGE UNL" in client.get("/").content.decode()


def test_login_sso_devuelve_identidad_y_rol():
    client = Client()
    valid = client.post(
        "/api/v1/auth/login-sso",
        data=json.dumps({"credential": "valid-sso-token"}),
        content_type="application/json",
    )
    assert valid.status_code == 200
    assert valid.json()["data"]["role"] == "UAI"

    invalid = client.post(
        "/api/v1/auth/login-sso",
        data=json.dumps({"credential": "credencial-invalida"}),
        content_type="application/json",
    )
    assert invalid.status_code == 409
    assert invalid.json()["errors"]["code"] == "BUSINESS_RULE_VIOLATION"
    assert invalid.json()["success"] is False


def test_recommendation_flow_returns_universal_envelope():
    client = Client()
    report_id = _create_report(client)
    created = _post(
        client,
        "/api/v1/recomendaciones",
        {
            "report_id": report_id,
            "number": "R-HTTP-001",
            "description": "Implementar control institucional",
            "unit_id": "UAI",
            "legal_days": 30,
            "due_date": "2026-12-31",
        },
    )
    assert created.status_code == 201, created.content
    body = created.json()
    assert body["success"] is True
    assert body["meta"]["request_id"]
    recommendation_id = body["data"]["id"]

    listed = client.get(
        "/api/v1/recomendaciones",
        HTTP_X_ROLE="UAI",
        HTTP_X_USER_ID="uai-http",
        HTTP_X_UNIT_ID="UAI",
    )
    assert listed.status_code == 200
    assert any(item["id"] == recommendation_id for item in listed.json()["data"])

    detail = client.get(
        f"/api/v1/recomendaciones/{recommendation_id}",
        HTTP_X_ROLE="UAI",
        HTTP_X_USER_ID="uai-http",
        HTTP_X_UNIT_ID="UAI",
    )
    assert detail.status_code == 200
    assert detail.json()["data"]["evidencias"] == []


def test_report_and_plan_routes_are_available():
    client = Client()
    report_id = _create_report(client, "INF-HTTP-002")
    recommendation = _post(
        client,
        "/api/v1/recomendaciones",
        {
            "report_id": report_id,
            "number": "R-HTTP-002",
            "description": "Actualizar controles",
            "unit_id": "UAI",
            "legal_days": 30,
            "due_date": "2026-12-31",
        },
    )
    recommendation_id = recommendation.json()["data"]["id"]

    plan = _post(
        client,
        f"/api/v1/recomendaciones/{recommendation_id}/plan-accion",
        {"descripcion_hito": "Presentar plan", "fecha_compromiso": "2026-11-01"},
        role="EJECUTOR",
        user="ejecutor-http",
        unit="UAI",
    )
    assert plan.status_code == 201, plan.content
    assert plan.json()["data"]["recommendation_id"] == recommendation_id

    detail = client.get(
        f"/api/v1/recomendaciones/{recommendation_id}",
        HTTP_X_ROLE="UAI",
        HTTP_X_USER_ID="uai-http",
        HTTP_X_UNIT_ID="UAI",
    )
    assert detail.json()["data"]["state"] == "EN_EJECUCION"
