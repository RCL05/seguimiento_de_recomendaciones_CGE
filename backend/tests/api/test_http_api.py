import json

import pytest
from django.test import Client, override_settings

from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter
from backend.modules.usuarios.models import UnidadOrganica
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db


def _post(client, path, payload, role="UAI", user="uai-http", unit="UAI"):
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        **authenticated_headers(role, user, unit),
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


def test_login_sso_devuelve_jwt_con_claims_de_identidad(monkeypatch):
    client = Client()
    sso_identity = {
        "correo": "jwt-login@unl.edu.ec",
        "nombres": "Usuario JWT",
        "rol": "UAI",
        "unidad_codigo": "UAI",
    }
    monkeypatch.setattr(
        "backend.modules.usuarios.infrastructure.sso_adapter.SsoAdapter.authenticate",
        lambda _adapter, *, token: sso_identity if token == "active-test-credential" else {},
    )
    valid = client.post(
        "/api/v1/sesiones",
        data=json.dumps({"credential": "active-test-credential"}),
        content_type="application/json",
    )
    assert valid.status_code == 200
    assert valid.json()["data"]["role"] == "UAI"
    data = valid.json()["data"]
    claims = SsoAdapter().validate_session(data["access_token"])
    assert claims["user_id"] == data["user_id"]
    assert claims["correo"] == "jwt-login@unl.edu.ec"
    assert claims["rol"] == "UAI"
    assert claims["unidad_codigo"] == "UAI"
    assert data["expires_in"] == SsoAdapter.token_ttl_seconds

    invalid = client.post(
        "/api/v1/sesiones",
        data=json.dumps({"credential": "credencial-invalida"}),
        content_type="application/json",
    )
    assert invalid.status_code == 401
    assert invalid.json()["errors"]["code"] == "AUTHENTICATION_REQUIRED"
    assert invalid.json()["success"] is False


def test_peticion_sin_token_responde_401_authentication_required():
    response = Client().get("/api/v1/recomendaciones")
    assert response.status_code == 401
    assert response.json()["errors"]["code"] == "AUTHENTICATION_REQUIRED"


@override_settings(DEBUG=True)
def test_rectorado_inicia_sesion_y_consulta_tablero():
    client = Client()
    login = client.post(
        "/api/v1/sesiones",
        data=json.dumps({"credential": "rectorado-sso-token"}),
        content_type="application/json",
    )
    assert login.status_code == 200, login.content
    assert login.json()["data"]["role"] == "RECTORADO"

    token = login.json()["data"]["access_token"]
    tablero = client.get(
        "/api/v1/reportes/tablero",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert tablero.status_code == 200, tablero.content
    assert "semaforo_riesgo" in tablero.json()["data"]


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
        **authenticated_headers("UAI", "uai-http", "UAI"),
    )
    assert listed.status_code == 200
    assert any(item["id"] == recommendation_id for item in listed.json()["data"])

    detail = client.get(
        f"/api/v1/recomendaciones/{recommendation_id}",
        **authenticated_headers("UAI", "uai-http", "UAI"),
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
        f"/api/v1/recomendaciones/{recommendation_id}/hitos",
        {"descripcion_hito": "Presentar plan", "fecha_compromiso": "2026-11-01"},
        role="EJECUTOR",
        user="ejecutor-http",
        unit="UAI",
    )
    assert plan.status_code == 201, plan.content
    assert plan.json()["data"]["recommendation_id"] == recommendation_id

    detail = client.get(
        f"/api/v1/recomendaciones/{recommendation_id}",
        **authenticated_headers("UAI", "uai-http", "UAI"),
    )
    assert detail.json()["data"]["state"] == "EN_PROCESO"


def test_evidence_requires_plan_then_moves_to_review_and_locks_plan(tmp_path):
    client = Client()
    report_id = _create_report(client, "INF-EVIDENCE-STATE")
    recommendation = _post(
        client,
        "/api/v1/recomendaciones",
        {
            "report_id": report_id,
            "number": "R-EVIDENCE-STATE",
            "description": "Registrar controles",
            "unit_id": "UAI",
            "legal_days": 30,
            "due_date": "2026-12-31",
        },
    ).json()["data"]
    recommendation_id = recommendation["id"]
    executor_headers = authenticated_headers("EJECUTOR", "evidence-state-executor", "UAI")
    pdf = b"%PDF-1.4\ncontenido de prueba"

    with override_settings(MEDIA_ROOT=tmp_path):
        pending_upload = client.post(
            f"/api/v1/recomendaciones/{recommendation_id}/evidencias",
            data=pdf,
            content_type="application/pdf",
            HTTP_X_FILENAME="evidencia.pdf",
            **executor_headers,
        )
        assert pending_upload.status_code == 409
        assert "Plan de accion" in pending_upload.json()["errors"]["detail"]

        plan = client.post(
            f"/api/v1/recomendaciones/{recommendation_id}/hitos",
            data=json.dumps({
                "descripcion_hito": "Aplicar control",
                "fecha_compromiso": "2026-11-30",
            }),
            content_type="application/json",
            **executor_headers,
        )
        assert plan.status_code == 201, plan.content

        uploaded = client.post(
            f"/api/v1/recomendaciones/{recommendation_id}/evidencias",
            data=pdf,
            content_type="application/pdf",
            HTTP_X_FILENAME="evidencia.pdf",
            **executor_headers,
        )
        assert uploaded.status_code == 201, uploaded.content

    detail = client.get(
        f"/api/v1/recomendaciones/{recommendation_id}",
        **authenticated_headers("UAI", "uai-http", "UAI"),
    )
    assert detail.json()["data"]["state"] == "EN_VALIDACION"

    locked_plan = client.post(
        f"/api/v1/recomendaciones/{recommendation_id}/hitos",
        data=json.dumps({
            "descripcion_hito": "Otro hito",
            "fecha_compromiso": "2026-12-01",
        }),
        content_type="application/json",
        **executor_headers,
    )
    assert locked_plan.status_code == 409


def test_units_endpoint_returns_full_catalog_with_model_field_names():
    inactive = UnidadOrganica.objects.create(
        codigo="OLD-UNIT",
        nombre="Unidad desactivada",
        activo=False,
    )
    response = Client().get(
        "/api/v1/unidades",
        **authenticated_headers("UAI", "uai-units", "UAI"),
    )
    assert response.status_code == 200, response.content
    units = response.json()["data"]
    assert {"id": str(inactive.id), "codigo": "OLD-UNIT", "nombre": "Unidad desactivada"} in units
