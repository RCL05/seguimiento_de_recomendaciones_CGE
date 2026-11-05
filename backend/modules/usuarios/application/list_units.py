"""Caso de uso para listar el catálogo de unidades orgánicas."""

from backend.core.shared.domain_types import PermissionDenied, Role
from backend.modules.usuarios.models import UnidadOrganica, Usuario

# UAI asigna recomendaciones a unidades; DTI administra la estructura orgánica (HU-6).
ROLES_CATALOGO = {Role.UAI.value, Role.DTI.value}


class ListUnits:
    def execute(self, *, actor: Usuario):
        if actor.rol not in ROLES_CATALOGO:
            raise PermissionDenied("Solo UAI o DTI pueden consultar el catálogo de unidades.")
        return UnidadOrganica.objects.all().order_by("codigo")
