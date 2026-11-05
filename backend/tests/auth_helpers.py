"""Utilities for authenticating API tests with real, signed JWTs."""

from __future__ import annotations


def authenticated_headers(
    role: str,
    user_key: str,
    unit_code: str | None = None,
) -> dict[str, str]:
    from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter
    from backend.modules.usuarios.models import UnidadOrganica, Usuario

    unit = None
    if unit_code:
        unit, _ = UnidadOrganica.objects.get_or_create(
            codigo=unit_code,
            defaults={"nombre": unit_code},
        )

    email = user_key if "@" in user_key else f"{user_key}@unl.edu.ec"
    user, _ = Usuario.objects.get_or_create(
        correo_institucional=email,
        defaults={
            "nombres": user_key,
            "rol": role,
            "unidad_org": unit,
            "activo": True,
        },
    )
    fields_to_update = []
    if user.rol != role:
        user.rol = role
        fields_to_update.append("rol")
    if user.unidad_org_id != (unit.id if unit else None):
        user.unidad_org = unit
        fields_to_update.append("unidad_org")
    if not user.activo:
        user.activo = True
        fields_to_update.append("activo")
    if fields_to_update:
        user.save(update_fields=fields_to_update)

    token = SsoAdapter().issue_session(
        {
            "user_id": str(user.id),
            "email": user.correo_institucional,
            "role": user.rol,
            "unit_id": user.unidad_org.codigo if user.unidad_org_id else None,
        }
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def authenticated_header(role: str, user_key: str, unit_code: str | None = None) -> str:
    return authenticated_headers(role, user_key, unit_code)["HTTP_AUTHORIZATION"]
