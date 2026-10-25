from dataclasses import dataclass


@dataclass(frozen=True)
class SsoIdentity:
    subject: str
    email: str
    display_name: str


class SsoAdapter:
    """Puerto mínimo; el proveedor institucional se inyecta en despliegue."""

    def authenticate(self, credential: str) -> SsoIdentity:
        if not credential:
            raise ValueError("La credencial institucional es obligatoria.")
        return SsoIdentity(
            subject="development-user",
            email="development-user@unl.edu.ec",
            display_name="Usuario institucional",
        )
