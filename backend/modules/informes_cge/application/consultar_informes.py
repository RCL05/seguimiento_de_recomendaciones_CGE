"""Casos de uso de consulta de informes CGE (solo lectura)."""
from uuid import UUID

from django.core.paginator import EmptyPage, Paginator

from backend.core.shared.domain_types import NotFoundError, PermissionDenied, ValidationError
from backend.modules.recomendaciones.models import InformeCGE
from backend.modules.usuarios.models import Usuario

# UAI registra los informes; Rectorado y el auditor CGE los consultan (RF-018).
ROLES_CONSULTA = {Usuario.Rol.UAI, Usuario.Rol.RECTORADO, Usuario.Rol.CGE_AUDITOR}
MAX_PAGE_SIZE = 100


def _authorize(actor: Usuario) -> None:
    if actor.rol not in ROLES_CONSULTA:
        raise PermissionDenied("No tiene permisos para consultar informes CGE.")


class ListarInformes:
    def execute(self, *, actor: Usuario, page: int = 1, page_size: int = 25):
        _authorize(actor)
        if page < 1 or not 1 <= page_size <= MAX_PAGE_SIZE:
            raise ValidationError(f"page debe ser >= 1 y page_size estar entre 1 y {MAX_PAGE_SIZE}.")
        queryset = InformeCGE.objects.order_by("-fecha_notificacion", "numero_informe")
        try:
            return Paginator(queryset, page_size).page(page)
        except EmptyPage as error:
            raise ValidationError("La página solicitada está fuera de rango.") from error


class ObtenerInforme:
    def execute(self, *, actor: Usuario, informe_id: UUID) -> InformeCGE:
        _authorize(actor)
        informe = InformeCGE.objects.filter(pk=informe_id).first()
        if informe is None:
            raise NotFoundError("El informe no existe.")
        return informe
