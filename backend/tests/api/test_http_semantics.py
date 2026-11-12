"""Semántica HTTP de la API (RFC 9110): métodos, códigos, Location, Allow y CORS."""

import json

import pytest
from django.test import Client

from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db

VITE_ORIGIN = "http://localhost:5173"


def _uai():
    return authenticated_headers("UAI", "uai-semantica", "UAI")


def _create_report(client, headers, number="INF-SEM-001"):
    response = client.post(
        "/api/v1/informes",
        data=json.dumps(
            {
                "numero_informe": number,
                "periodo_auditado": "2026",
                "fecha_notificacion": "2026-01-10",
                "pdf_informe_url": "https://example.test/informe.pdf",
            }
        ),
        content_type="application/json",
        **headers,
    )
    assert response.status_code == 201, response.content
    return response.json()["data"]["id"]


def _create_recommendation(client, headers):
    report_id = _create_report(client, headers)
    return client.post(
        "/api/v1/recomendaciones",
        data=json.dumps(
            {
                "report_id": report_id,
                "number": "R-SEM-001",
                "description": "Control institucional",
                "unit_id": "UAI",
                "legal_days": 30,
                "due_date": "2027-01-10",
            }
        ),
        content_type="application/json",
        **headers,
    )


def test_201_incluye_location_del_recurso_creado():
    client, headers = Client(), _uai()
    created = _create_recommendation(client, headers)

    assert created.status_code == 201
    recommendation_id = created.json()["data"]["id"]
    assert created["Location"] == f"/api/v1/recomendaciones/{recommendation_id}"
    assert client.get(created["Location"], **headers).status_code == 200


def test_json_mal_formado_responde_400_validation_error():
    response = Client().post(
        "/api/v1/recomendaciones",
        data="{no-es-json",
        content_type="application/json",
        **_uai(),
    )
    assert response.status_code == 400
    assert response.json()["errors"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    ("method", "path", "allowed"),
    [
        ("put", "/api/v1/recomendaciones/{rid}", {"GET", "HEAD", "PATCH"}),
        ("delete", "/api/v1/recomendaciones/{rid}", {"GET", "HEAD", "PATCH"}),
        ("delete", "/api/v1/recomendaciones", {"GET", "HEAD", "POST"}),
        ("put", "/api/v1/unidades", {"GET", "HEAD", "POST"}),
        ("get", "/api/v1/sesiones", {"POST"}),
        ("post", "/api/v1/reportes/matriz-cge", {"GET", "HEAD"}),
        ("patch", "/api/v1/recomendaciones/{rid}/dictamenes", {"POST"}),
    ],
)
def test_metodo_no_admitido_responde_405_con_allow(method, path, allowed):
    # DRF implementa OPTIONS en todos los recursos, por eso también aparece en Allow.
    allowed = allowed | {"OPTIONS"}
    client, headers = Client(), _uai()
    recommendation_id = _create_recommendation(client, headers).json()["data"]["id"]

    response = getattr(client, method)(path.format(rid=recommendation_id), **headers)

    assert response.status_code == 405
    assert {item.strip() for item in response["Allow"].split(",")} == allowed
    body = response.json()
    assert body["success"] is False and body["data"] is None
    assert body["errors"]["code"] == "METHOD_NOT_ALLOWED"


def test_405_se_evalua_antes_que_la_autenticacion():
    response = Client().put("/api/v1/recomendaciones")
    assert response.status_code == 405
    assert "GET" in response["Allow"]


@pytest.mark.parametrize("limit", ["abc", "0", "501"])
def test_limit_invalido_en_auditoria_responde_400(limit):
    response = Client().get(f"/api/v1/auditoria?limit={limit}", **_uai())
    assert response.status_code == 400
    assert response.json()["errors"]["code"] == "VALIDATION_ERROR"


def test_preflight_cors_desde_origen_autorizado():
    response = Client().options(
        "/api/v1/recomendaciones",
        HTTP_ORIGIN=VITE_ORIGIN,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
    )
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == VITE_ORIGIN
    assert "authorization" in response["Access-Control-Allow-Headers"].lower()


def test_cors_expone_location_y_rechaza_origen_no_autorizado():
    client, headers = Client(), _uai()
    allowed = client.get("/api/v1/recomendaciones", HTTP_ORIGIN=VITE_ORIGIN, **headers)
    assert allowed["Access-Control-Allow-Origin"] == VITE_ORIGIN
    assert "Location" in allowed["Access-Control-Expose-Headers"]

    foreign = client.get("/api/v1/recomendaciones", HTTP_ORIGIN="https://evil.example", **headers)
    assert not foreign.has_header("Access-Control-Allow-Origin")
