import json
import uuid

import pytest
from django.test import Client

from backend.core.audit.models import AuditLog
from backend.modules.usuarios.models import UnidadOrganica

pytestmark = pytest.mark.django_db


def _create_recommendation(client: Client) -> str:
    for codigo in ("DEP-A", "DEP-B"):
        UnidadOrganica.objects.get_or_create(
            id=uuid.uuid5(uuid.NAMESPACE_URL, f"sitra-unit:{codigo}"),
            defaults={"codigo": codigo, "nombre": codigo},
        )

    report = client.post(
        "/api/v1/informes",
        data=json.dumps(
            {
                "numero_informe": "INF-BOLA-001",
                "periodo_auditado": "2026",
                "fecha_notificacion": "2026-01-10",
                "pdf_informe_url": "https://example.test/informe.pdf",
            }
        ),
        content_type="application/json",
        HTTP_X_ROLE="UAI",
        HTTP_X_USER_ID="uai-bola",
        HTTP_X_UNIT_ID="UAI",
    )
    assert report.status_code == 201
    recommendation = client.post(
        "/api/v1/recomendaciones",
        data=json.dumps(
            {
                "report_id": report.json()["data"]["id"],
                "number": "REC-BOLA-001",
                "description": "Control interno",
                "unit_id": "DEP-A",
                "legal_days": 30,
                "due_date": "2026-02-14",
            }
        ),
        content_type="application/json",
        HTTP_X_ROLE="UAI",
        HTTP_X_USER_ID="uai-bola",
        HTTP_X_UNIT_ID="UAI",
    )
    assert recommendation.status_code == 201
    return recommendation.json()["data"]["id"]


def test_bola_idor_entre_unidades_retorna_404_sin_revelar_existencia_y_audita():
    client = Client()
    recommendation_id = _create_recommendation(client)

    response = client.get(
        f"/api/v1/recomendaciones/{recommendation_id}",
        HTTP_X_ROLE="EJECUTOR",
        HTTP_X_USER_ID="ejecutor-dep-b",
        HTTP_X_UNIT_ID="DEP-B",
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["errors"]["code"] == "RESOURCE_NOT_FOUND"
    assert "DEP-A" not in body["message"]

    denied = AuditLog.objects.get(
        entidad_id=recommendation_id,
        accion="ACCESS_DENIED",
    )
    assert denied.resultado == "DENIED"
    assert denied.detalles_json["reason"] == "different_unit"
    assert denied.request_id


def test_recurso_inexistente_tambien_retorna_404_estructurado():
    response = Client().get(
        "/api/v1/recomendaciones/00000000-0000-0000-0000-000000000999",
        HTTP_X_ROLE="UAI",
        HTTP_X_USER_ID="uai-bola",
        HTTP_X_UNIT_ID="UAI",
    )

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["errors"]["code"] == "RESOURCE_NOT_FOUND"
