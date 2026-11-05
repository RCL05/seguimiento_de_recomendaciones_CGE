from typing import Protocol

from backend.core.shared.domain_types import Role, User


class IdentityProvider(Protocol):
    def authenticate(self, credential: str) -> User:
        ...


class AuthorizationPolicy(Protocol):
    def can_access_recommendation(self, user: User, unit_id: str) -> bool:
        ...


class RoleRepository(Protocol):
    def assign(self, user_id: str, role: Role) -> None:
        ...
