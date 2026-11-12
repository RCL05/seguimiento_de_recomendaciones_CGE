"""Segregación de funciones por rol (RF-001, RF-002) y vigencia de la identidad en cada petición."""

import json
from uuid import uuid4

import pytest
from django.test import Client

from backend.modules.usuarios.models import Usuario
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db

ROLES = {
    "UAI": ("UAI", "uai-roles", "UAI"),
    "EJECUTOR": ("EJECUTOR", "ejecutor-roles", "DEP-A"),
    "DTI": ("DTI", "dti-roles", None),
    "RECTORADO": ("RECTORADO", "rectorado-roles", None),
    "CGE_AUDITOR": ("CGE_AUDITOR", "cge-roles", None),
}

# (método, ruta, roles autorizados). Con un cuerpo vacío, un rol autorizado supera el
# permiso y llega a la validación (400); uno no autorizado se detiene antes (403).
OPERACIONES = [
    ("post", "/api/v1/recomendaciones", {"UAI"}),
    ("post", "/api/v1/informes", {"UAI"}),
    ("post", "/api/v1/unidades", {"DTI"}),
    ("post", f"/api/v1/recomendaciones/{uuid4()}/dictamenes", {"UAI"}),
    ("post", f"/api/v1/recomendaciones/{uuid4()}/hitos", {"EJECUTOR"}),
]


def _llamar(metodo, ruta, rol):
    headers = authenticated_headers(*ROLES[rol])
    return getattr(Client(), metodo)(ruta, data=json.dumps({}), content_type="application/json", **headers)


@pytest.mark.parametrize(("metodo", "ruta", "autorizados"), OPERACIONES)
@pytest.mark.parametrize("rol", sorted(ROLES))
def test_cada_operacion_solo_la_ejecuta_su_rol(metodo, ruta, autorizados, rol):
    response = _llamar(metodo, ruta, rol)

    if rol in autorizados:
        assert response.status_code == 400, response.content
    else:
        assert response.status_code == 403, response.content
        assert response.json()["errors"]["code"] == "PERMISSION_DENIED"


@pytest.mark.parametrize("rol", sorted(ROLES))
def test_auditoria_solo_para_uai_y_auditor_cge(rol):
    headers = authenticated_headers(*ROLES[rol])

    response = Client().get("/api/v1/auditoria", **headers)

    assert response.status_code == (200 if rol in {"UAI", "CGE_AUDITOR"} else 403)


def test_token_de_una_cuenta_desactivada_deja_de_valer():
    headers = authenticated_headers(*ROLES["UAI"])
    assert Client().get("/api/v1/recomendaciones", **headers).status_code == 200

    Usuario.objects.filter(correo_institucional="uai-roles@unl.edu.ec").update(activo=False)

    response = Client().get("/api/v1/recomendaciones", **headers)
    assert response.status_code == 401
    assert response["WWW-Authenticate"].startswith("Bearer")


def test_token_con_rol_cambiado_por_dti_deja_de_valer():
    headers = authenticated_headers(*ROLES["UAI"])

    Usuario.objects.filter(correo_institucional="uai-roles@unl.edu.ec").update(rol=Usuario.Rol.RECTORADO)

    assert Client().get("/api/v1/recomendaciones", **headers).status_code == 401
