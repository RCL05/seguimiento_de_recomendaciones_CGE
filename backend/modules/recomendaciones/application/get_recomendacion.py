"""Caso de uso para consultar una recomendación y sus evidencias."""

from uuid import UUID

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import NotFoundError, PermissionDenied
from backend.modules.recomendaciones.application.list_recomendaciones import ALLOWED_ROLES
from backend.modules.recomendaciones.infrastructure.repositories import RecommendationRepository
from backend.modules.usuarios.models import Usuario


class GetRecomendacion:
    def __init__(self, repository: RecommendationRepository | None = None) -> None:
        self._repository = repository or RecommendationRepository()

    def execute(
        self,
        *,
        actor: Usuario,
        recommendation_id: UUID,
        request_id: str,
        ip_address: str | None = None,
    ):
        if actor.rol not in ALLOWED_ROLES:
            raise PermissionDenied("No tiene permisos para consultar recomendaciones.")

        recommendation = self._repository.get_detail(recommendation_id)
        if recommendation is None:
            raise NotFoundError("La recomendación no existe.")

        if (
            actor.rol == Usuario.Rol.EJECUTOR
            and actor.unidad_org_id != recommendation.unidad_responsable_id
        ):
            record_audit(
                request_id=request_id,
                user=actor,
                action="ACCESS_DENIED",
                entity="recommendation",
                entity_id=recommendation.id,
                details={"reason": "different_unit", "result": "not_found"},
                resultado="DENIED",
                ip_address=ip_address,
            )
            raise NotFoundError("La recomendación no existe.")
        return recommendation
