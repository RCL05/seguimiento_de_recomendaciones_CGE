from __future__ import annotations

from uuid import UUID

from backend.modules.recomendaciones.models import DictamenUAI, Evidencia, Recomendacion
from backend.modules.usuarios.models import Usuario


class DictamenRepository:
    @staticmethod
    def create(
        *,
        recomendacion: Recomendacion,
        evidencia: Evidencia | None = None,
        evaluador: Usuario,
        resultado: str,
        observaciones_oficiales: str = "",
    ) -> DictamenUAI:
        return DictamenUAI.objects.create(
            recomendacion=recomendacion,
            evidencia=evidencia,
            evaluador=evaluador,
            resultado=resultado,
            observaciones_oficiales=observaciones_oficiales,
        )

    @staticmethod
    def get_by_recomendacion(recomendacion_id: UUID):
        return DictamenUAI.objects.filter(recomendacion_id=recomendacion_id).order_by(
            "-fecha_dictamen"
        )
