"""Contrato de la API: envoltura universal y sincronía OpenAPI <-> código (RF-022)."""
from pathlib import Path

import pytest
import yaml
from django.urls import URLPattern, URLResolver, get_resolver
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema

REPO = Path(__file__).resolve().parents[3]
# Fuente oficial (backend) y copia enlazada desde los artefactos Spec Kit (plan, tasks, quickstart).
CONTRACTS = [
    REPO / "backend" / "contracts" / "openapi.yaml",
    REPO / "specs" / "001-seguimiento-recomendaciones" / "contracts" / "openapi.yaml",
]
REGENERATE = (
    "python backend/manage.py spectacular --validate --fail-on-warn --file backend/contracts/openapi.yaml\n"
    "  copy backend/contracts/openapi.yaml specs/001-seguimiento-recomendaciones/contracts/openapi.yaml"
)


def test_contract_envoltorio_exitoso_y_error():
    from backend.core.api.response_envelope import build_envelope

    ok = build_envelope(success=True, message="ok", data={"id": "1"})
    err = build_envelope(success=False, message="bad", errors={"code": "VALIDATION_ERROR"})
    assert ok["success"] is True and ok["errors"] is None
    assert err["success"] is False and err["data"] is None
    assert err["errors"]["code"] == "VALIDATION_ERROR"


@pytest.fixture(scope="module")
def generated_schema():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    validate_schema(schema)
    # Normaliza tipos (UUID, Decimal, etc.) igual que el archivo publicado.
    return yaml.safe_load(yaml.safe_dump(schema, allow_unicode=True, sort_keys=False))


@pytest.mark.parametrize("contract", CONTRACTS, ids=lambda path: str(path.relative_to(REPO)))
def test_contrato_publicado_coincide_con_el_codigo(generated_schema, contract):
    published = yaml.safe_load(contract.read_text(encoding="utf-8"))
    assert published == generated_schema, (
        f"{contract.relative_to(REPO)} está desactualizado. Regenérelo con:\n  {REGENERATE}"
    )


def _api_routes(resolver=None, prefix=""):
    resolver = resolver or get_resolver()
    for pattern in resolver.url_patterns:
        route = prefix + str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            yield from _api_routes(pattern, route)
        elif isinstance(pattern, URLPattern) and route.startswith("api/v1/"):
            yield "/" + route.replace("<uuid:", "{").replace(">", "}")


def test_toda_ruta_api_v1_esta_documentada(generated_schema):
    documented = set(generated_schema["paths"])
    missing = sorted(set(_api_routes()) - documented)
    assert not missing, f"Rutas sin documentar en OpenAPI: {missing}"


def test_operaciones_protegidas_declaran_bearer_y_401(generated_schema):
    publicas = {("/api/v1/auth/login-sso", "post")}
    for path, operations in generated_schema["paths"].items():
        if not path.startswith("/api/v1/"):
            continue
        for method, operation in operations.items():
            if (path, method) in publicas:
                continue
            assert {"bearerAuth": []} in operation.get("security", []), f"{method.upper()} {path} sin bearerAuth"
            assert "401" in operation["responses"], f"{method.upper()} {path} no documenta 401"
