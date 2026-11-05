"""Autenticación DRF con JWT Bearer emitido por el login SSO (ADR-0002).

El token se valida en cada petición contra la cuenta activa: si el rol o la
unidad cambiaron después de emitirlo, deja de ser válido.
"""
from __future__ import annotations

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from backend.core.shared.domain_types import Role
from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter
from backend.modules.usuarios.models import Usuario


class JWTBearerAuthentication(BaseAuthentication):
    """Resuelve `Authorization: Bearer <jwt>` a un `Usuario` activo.

    Sin cabecera devuelve `None`; la permisología responde entonces 401.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header:
            return None
        scheme, _, token = header.partition(" ")
        token = token.strip()
        if scheme.lower() != self.keyword.lower() or not token:
            raise AuthenticationFailed("Se requiere un token Bearer válido.")

        identity = SsoAdapter().validate_session(token)
        if not identity or not identity.get("user_id"):
            raise AuthenticationFailed("El token de sesión no es válido o expiró.")

        actor = (
            Usuario.objects.select_related("unidad_org")
            .filter(
                pk=identity["user_id"],
                correo_institucional=identity["correo"],
                activo=True,
            )
            .first()
        )
        if actor is None:
            raise AuthenticationFailed("La identidad no está habilitada en el sistema.")
        try:
            role = Role(identity["rol"])
        except ValueError as error:
            raise AuthenticationFailed("El rol registrado no es válido.") from error

        current_unit = actor.unidad_org.codigo if actor.unidad_org_id else None
        if actor.rol != role.value or current_unit != identity.get("unidad_codigo"):
            raise AuthenticationFailed(
                "Los permisos del token ya no coinciden con la cuenta activa."
            )
        return actor, identity

    def authenticate_header(self, request):
        # Presente => DRF responde 401 (no 403) cuando falta o falla la autenticación.
        return f'{self.keyword} realm="sitra-cge"'
