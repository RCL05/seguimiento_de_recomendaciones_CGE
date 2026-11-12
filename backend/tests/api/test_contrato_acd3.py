"""Ajustes del contrato acordados en la ACD 3 (clínica de arquitectura y contrato API)."""

import json
from uuid import uuid4

import pytest
from django.test import Client

from tests.api.test_endpoints_base import _json, ejecutor, informe, recomendacion_en_validacion, uai  # noqa: F401
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db

PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


def _recomendacion(uai, informe, **cambios):  # noqa: F811
    payload = {
        "report_id": informe.json()["data"]["id"],
        "number": "R-ACD3-1",
        "description": "Implementar control interno.",
        "unit_id": "DEP-A",
        "legal_days": 30,
        "due_date": "2027-06-30",
    }
    payload.update(cambios)
    return _json(Client(), "post", "/api/v1/recomendaciones", payload, uai)


# --- Sesiones ----------------------------------------------------------------


# POST /sesiones (credencial válida e inválida) se prueba en tests/api/test_http_api.py.


def test_la_ruta_de_accion_login_sso_ya_no_existe():
    response = Client().post(
        "/api/v1/auth/login-sso",
        data=json.dumps({"credential": "uai-sso-token"}),
        content_type="application/json",
    )
    assert response.status_code == 404


# --- Hitos ---------------------------------------------------------------------


def test_hitos_se_crean_y_consultan_como_recurso(uai, ejecutor, informe):  # noqa: F811
    rec_id = _recomendacion(uai, informe).json()["data"]["id"]

    creado = _json(
        Client(),
        "post",
        f"/api/v1/recomendaciones/{rec_id}/hitos",
        {"descripcion_hito": "Redactar propuesta", "fecha_compromiso": "2027-03-01"},
        ejecutor,
    )
    assert creado.status_code == 201, creado.content
    assert creado["Location"] == f"/api/v1/recomendaciones/{rec_id}/hitos"

    lista = Client().get(f"/api/v1/recomendaciones/{rec_id}/hitos", **ejecutor)
    assert [h["id"] for h in lista.json()["data"]] == [creado.json()["data"]["id"]]


def test_la_ruta_plan_accion_ya_no_existe(uai, ejecutor, informe):  # noqa: F811
    rec_id = _recomendacion(uai, informe).json()["data"]["id"]
    response = Client().get(f"/api/v1/recomendaciones/{rec_id}/plan-accion", **ejecutor)
    assert response.status_code == 404


# --- Referencias inexistentes: 400 con el campo inválido ---------------------


def test_informe_inexistente_responde_400_con_el_campo(uai, ejecutor, informe):  # noqa: F811
    response = _recomendacion(uai, informe, report_id=str(uuid4()))

    assert response.status_code == 400
    errors = response.json()["errors"]
    assert errors["code"] == "VALIDATION_ERROR"
    assert list(errors["fields"]) == ["report_id"]


def test_unidad_inexistente_responde_400_con_el_campo(uai, informe):  # noqa: F811
    response = _recomendacion(uai, informe, unit_id="NO-EXISTE")

    assert response.status_code == 400
    assert list(response.json()["errors"]["fields"]) == ["unit_id"]


def test_numero_repetido_sigue_siendo_409(uai, ejecutor, informe):  # noqa: F811
    assert _recomendacion(uai, informe).status_code == 201
    response = _recomendacion(uai, informe)
    assert response.status_code == 409
    assert response.json()["errors"]["code"] == "CONFLICT"


# --- Evidencia sin plan: 409 ----------------------------------------------------


def test_evidencia_sin_plan_responde_409(uai, ejecutor, informe):  # noqa: F811
    rec_id = _recomendacion(uai, informe).json()["data"]["id"]

    response = Client().post(
        f"/api/v1/recomendaciones/{rec_id}/evidencias",
        data=PDF,
        content_type="application/pdf",
        HTTP_X_FILENAME="evidencia.pdf",
        **ejecutor,
    )

    assert response.status_code == 409
    assert response.json()["errors"]["code"] == "CONFLICT"


# --- Dictamen: Location y consulta -------------------------------------------


def test_dictamen_201_con_location_que_se_puede_consultar(recomendacion_en_validacion, uai, ejecutor):  # noqa: F811
    rec_id, evidencia, _ = recomendacion_en_validacion
    creado = _json(
        Client(),
        "post",
        f"/api/v1/recomendaciones/{rec_id}/dictamenes",
        {"evidence_id": evidencia["id"], "approved": False, "observaciones": "Falta la firma."},
        uai,
    )
    assert creado.status_code == 201, creado.content
    dictamen_id = creado.json()["data"]["id"]
    assert creado["Location"] == f"/api/v1/recomendaciones/{rec_id}/dictamenes/{dictamen_id}"

    for headers in (uai, ejecutor):
        consulta = Client().get(creado["Location"], **headers)
        assert consulta.status_code == 200, consulta.content
        assert consulta.json()["data"]["id"] == dictamen_id
        assert consulta.json()["data"]["resultado"] == "RECHAZADO"


def test_dictamen_no_visible_para_otra_unidad_ni_bajo_otra_recomendacion(
    recomendacion_en_validacion, uai, informe  # noqa: F811
):
    rec_id, evidencia, _ = recomendacion_en_validacion
    creado = _json(
        Client(),
        "post",
        f"/api/v1/recomendaciones/{rec_id}/dictamenes",
        {"evidence_id": evidencia["id"], "approved": False, "observaciones": "Incompleta."},
        uai,
    )
    dictamen_id = creado.json()["data"]["id"]

    ajeno = authenticated_headers("EJECUTOR", "ejecutor-ajeno-acd3", "DEP-B")
    assert Client().get(creado["Location"], **ajeno).status_code == 404

    otra = _recomendacion(uai, informe, number="R-ACD3-OTRA").json()["data"]["id"]
    cruzada = Client().get(f"/api/v1/recomendaciones/{otra}/dictamenes/{dictamen_id}", **uai)
    assert cruzada.status_code == 404


# --- Evaluación de plazos: solo comando programado --------------------------


def test_evaluaciones_plazos_ya_no_se_expone_en_la_api():
    dti = authenticated_headers("DTI", "dti-acd3")
    response = Client().post("/api/v1/evaluaciones-plazos", **dti)
    assert response.status_code == 404
