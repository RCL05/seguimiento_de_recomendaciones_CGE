"""Caso de uso para listar el catálogo de unidades orgánicas por UAI."""

from backend.core.shared.domain_types import PermissionDenied, Role
from backend.modules.usuarios.models import UnidadOrganica, Usuario


class ListUnits:
    def execute(self, *, actor: Usuario):
        if actor.rol != Role.UAI.value:
            raise PermissionDenied("Solo UAI puede consultar unidades asignables.")
        return UnidadOrganica.objects.all().order_by("codigo")
