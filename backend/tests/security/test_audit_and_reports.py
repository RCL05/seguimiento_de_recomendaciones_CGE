"""La bitácora se consulta por API pero no se modifica por ningún medio (RF-017, RF-020)."""

import json

import pytest
from django.test import Client

from backend.core.audit.audit_repository import AuditRepository
from backend.core.audit.models import AuditLog
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db


@pytest.fixture
def uai():
    return authenticated_headers("UAI", "uai-bitacora", "UAI")


@pytest.fixture
def registro(uai):
    """Una operación real que deja un registro en la bitácora."""
    response = Client().post(
        "/api/v1/informes",
        data=json.dumps(
            {
                "numero_informe": "INF-BITACORA-1",
                "periodo_auditado": "2025",
                "fecha_notificacion": "2026-01-10",
                "pdf_informe_url": "https://example.test/inf.pdf",
            }
        ),
        content_type="application/json",
        **uai,
    )
    assert response.status_code == 201, response.content
    return AuditLog.objects.latest("id")


@pytest.mark.parametrize("metodo", ["post", "put", "patch", "delete"])
def test_la_api_de_auditoria_no_admite_escrituras(uai, registro, metodo):
    antes = list(AuditLog.objects.values_list("id", "accion", "detalles_json"))

    response = getattr(Client(), metodo)(
        "/api/v1/auditoria", data=json.dumps({"accion": "BORRADO"}), content_type="application/json", **uai
    )

    assert response.status_code == 405
    assert response.json()["errors"]["code"] == "METHOD_NOT_ALLOWED"
    assert list(AuditLog.objects.values_list("id", "accion", "detalles_json")) == antes


def test_la_consulta_devuelve_el_registro_sin_alterarlo(uai, registro):
    response = Client().get("/api/v1/auditoria", **uai)

    assert response.status_code == 200
    assert any(item["id"] == registro.id for item in response.json()["data"])
    registro_despues = AuditLog.objects.get(pk=registro.pk)
    assert registro_despues.detalles_json == registro.detalles_json
    assert registro_despues.accion == registro.accion


def test_la_consulta_del_repositorio_filtra_por_entidad(registro):
    filtrados = AuditRepository.query_read_only(entity=registro.entidad, entity_id=registro.entidad_id)

    assert list(filtrados.values_list("id", flat=True)) == [registro.id]
