"""Caso de uso: consultar un dictamen UAI de una recomendación (RF-010).

La visibilidad es la de la recomendación: un ejecutor de otra unidad recibe 404
sin que se revele si el dictamen existe (RF-019).
"""
from __future__ import annotations

from uuid import UUID

from backend.core.shared.domain_types import NotFoundError
from backend.modules.recomendaciones.application.get_recomendacion import GetRecomendacion
from backend.modules.recomendaciones.models import DictamenUAI
from backend.modules.usuarios.models import Usuario


class GetDictamen:
    def execute(
        self,
        *,
        actor: Usuario,
        recommendation_id: UUID,
        dictamen_id: UUID,
        request_id: str,
        ip_address: str | None = None,
    ) -> DictamenUAI:
        recommendation = GetRecomendacion().execute(
            actor=actor,
            recommendation_id=recommendation_id,
            request_id=request_id,
            ip_address=ip_address,
        )
        dictamen = (
            DictamenUAI.objects.select_related("recomendacion__unidad_responsable")
            .filter(pk=dictamen_id, recomendacion=recommendation)
            .first()
        )
        if dictamen is None:
            raise NotFoundError("El dictamen no existe.")
        return dictamen
