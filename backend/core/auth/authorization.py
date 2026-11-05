from ..shared.domain_types import PermissionDenied, Role, User


def require_role(user: User, *roles: Role) -> None:
    if user.role not in roles:
        raise PermissionDenied("El usuario no tiene el rol requerido.")


def require_same_unit(user: User, unit_id: str) -> None:
    require_role(user, Role.EJECUTOR)
    if user.unit_id != unit_id:
        raise PermissionDenied("El recurso pertenece a otra dependencia.")
