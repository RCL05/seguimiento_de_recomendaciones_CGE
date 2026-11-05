"""Caso de uso para consultar recomendaciones visibles para un usuario."""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from datetime import date

from backend.core.shared.domain_types import PermissionDenied, ValidationError
from backend.modules.recomendaciones.infrastructure.repositories import RecommendationRepository
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario


ALLOWED_ROLES = {
    Usuario.Rol.EJECUTOR,
    Usuario.Rol.UAI,
    Usuario.Rol.RECTORADO,
    Usuario.Rol.CGE_AUDITOR,
}
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


class ListRecomendaciones:
    def __init__(self, repository: RecommendationRepository | None = None) -> None:
        self._repository = repository or RecommendationRepository()

    def execute(
        self,
        *,
        actor: Usuario,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        state: str | None = None,
        unit_code: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        due_before: str | None = None,
        due_after: str | None = None,
        overdue: bool | None = None,
    ):
        if actor.rol not in ALLOWED_ROLES:
            raise PermissionDenied("No tiene permisos para consultar recomendaciones.")
        if page < 1:
            raise ValidationError("El parámetro page debe ser mayor que cero.")
        if page_size < 1 or page_size > MAX_PAGE_SIZE:
            raise ValidationError(
                f"El parámetro page_size debe estar entre 1 y {MAX_PAGE_SIZE}."
            )
        if actor.rol == Usuario.Rol.EJECUTOR:
            if actor.unidad_org_id is None:
                queryset = self._repository.list_for_unit_code("")
            else:
                queryset = self._repository.list_for_unit_code(actor.unidad_org.codigo)
        else:
            queryset = self._repository.list_all()

        if state:
            state = state.strip().upper()
            if state not in Recomendacion.Estado.values:
                raise ValidationError("El filtro state no corresponde a un estado válido.")
        unit_code = unit_code.strip() if unit_code else None
        priority = priority.strip() if priority else None
        if unit_code == "" or priority == "":
            raise ValidationError("Los filtros unit_id y priority no pueden estar vacíos.")
        parsed_dates = {
            "due_date": _parse_date(due_date, "due_date"),
            "due_before": _parse_date(due_before, "due_before"),
            "due_after": _parse_date(due_after, "due_after"),
        }
        if (
            parsed_dates["due_before"]
            and parsed_dates["due_after"]
            and parsed_dates["due_after"] > parsed_dates["due_before"]
        ):
            raise ValidationError("due_after no puede ser posterior a due_before.")
        queryset = self._repository.filter_list(
            queryset,
            state=state,
            unit_code=unit_code,
            priority=priority,
            overdue=overdue,
            **parsed_dates,
        )

        paginator = Paginator(queryset, page_size)
        try:
            return paginator.page(page)
        except (EmptyPage, PageNotAnInteger) as error:
            raise ValidationError("La página solicitada está fuera de rango.") from error


def _parse_date(value: str | None, parameter: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValidationError(f"El filtro {parameter} debe tener formato YYYY-MM-DD.") from error
