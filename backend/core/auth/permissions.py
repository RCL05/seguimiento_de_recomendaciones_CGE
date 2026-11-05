"""Permisos DRF: autenticación obligatoria y RBAC por rol institucional.

La autorización a nivel de objeto (unidad responsable, BOLA/IDOR) permanece en
los casos de uso de aplicación, que conocen el recurso consultado.
"""
from __future__ import annotations

from rest_framework.permissions import BasePermission

from backend.core.shared.domain_types import Role


class IsAuthenticatedActor(BasePermission):
    """Exige un `Usuario` resuelto por `JWTBearerAuthentication`."""

    def has_permission(self, request, view):
        return request.auth is not None and request.user is not None


def require_roles(*roles: Role, message: str | None = None) -> type[BasePermission]:
    """Crea una clase de permiso que admite solo los roles indicados.

    Uso: ``permission_classes = [IsAuthenticatedActor, require_roles(Role.UAI)]``.
    """
    allowed = frozenset(role.value for role in roles)
    names = ", ".join(sorted(allowed))

    class HasRole(BasePermission):
        def has_permission(self, request, view):
            return getattr(request.user, "rol", None) in allowed

    HasRole.message = message or f"Esta operación requiere uno de los roles: {names}."
    HasRole.__name__ = f"HasRole_{'_'.join(sorted(allowed))}"
    HasRole.allowed_roles = allowed
    return HasRole
