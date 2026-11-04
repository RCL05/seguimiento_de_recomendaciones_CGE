import json
from urllib.parse import parse_qs

import pytest
from django.test import override_settings

from backend.modules.usuarios.models import Usuario


@pytest.mark.django_db
def test_sso_adapter_interpreta_claims_de_introspeccion(monkeypatch):
    from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter

    class IntrospectionResponse:
        def __init__(self, claims):
            self.claims = claims

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps(self.claims).encode()

    def introspect(request, timeout):
        assert timeout == 5
        credential = parse_qs(request.data.decode()).get("token", [""])[0]
        if credential == "opaque-uai-credential":
            return IntrospectionResponse(
                {
                    "active": True,
                    "email": "uai@unl.edu.ec",
                    "name": "Usuario UAI",
                    "role": "UAI",
                    "unit_id": "UAI",
                }
            )
        if credential == "opaque-dti-credential":
            return IntrospectionResponse(
                {
                    "active": True,
                    "email": "dti@unl.edu.ec",
                    "name": "Usuario DTI",
                    "role": "DTI",
                    "unit_id": "DTI",
                }
            )
        return IntrospectionResponse({"active": False})

    monkeypatch.setenv("SSO_INTROSPECTION_URL", "https://sso.example.test/introspect")
    monkeypatch.setenv("SSO_CLIENT_ID", "test-client")
    monkeypatch.setenv("SSO_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(
        "backend.modules.usuarios.infrastructure.sso_adapter.urlopen", introspect
    )
    sso = SsoAdapter()
    uai_identity = sso.authenticate(token="opaque-uai-credential")
    assert uai_identity["sub"]
    assert uai_identity["email"] == uai_identity["correo"] == "uai@unl.edu.ec"
    assert uai_identity["nombres"] == "Usuario UAI"
    assert uai_identity["rol"] == "UAI"
    assert uai_identity["unidad_id"]
    assert uai_identity["unidad_codigo"] == "UAI"
    assert sso.authenticate(token="opaque-dti-credential")["rol"] == "DTI"
    assert sso.authenticate(token="inactive-credential") == {}


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_tokens_sso_de_desarrollo_crean_identidades_completas():
    from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter

    adapter = SsoAdapter()
    expected = {
        "uai-sso-token": ("uai@unl.edu.ec", "UAI", "UAI"),
        "valid-sso-token": ("uai@unl.edu.ec", "UAI", "UAI"),
        "ejecutor-sso-token": ("ejecutor@unl.edu.ec", "EJECUTOR", "DEP-A"),
        "dti-sso-token": ("dti@unl.edu.ec", "DTI", "DTI"),
    }

    for token, (email, role, unit_code) in expected.items():
        identity = adapter.authenticate(token=token)
        user = Usuario.objects.select_related("unidad_org").get(
            correo_institucional=email
        )

        assert identity["sub"] == str(user.id)
        assert identity["email"] == email
        assert identity["nombres"] == user.nombres
        assert identity["rol"] == role == user.rol
        assert identity["unidad_id"] == str(user.unidad_org_id)
        assert identity["unidad_codigo"] == unit_code
        assert user.unidad_org.codigo == unit_code


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_tokens_de_desarrollo_no_se_aceptan_fuera_de_debug(monkeypatch):
    from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter

    for variable in ("SSO_INTROSPECTION_URL", "SSO_CLIENT_ID", "SSO_CLIENT_SECRET"):
        monkeypatch.delenv(variable, raising=False)

    assert SsoAdapter().authenticate(token="valid-sso-token") == {}
