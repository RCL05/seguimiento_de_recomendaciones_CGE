"""Caso de uso para abrir o descargar el PDF de una evidencia."""

from pathlib import Path
from uuid import UUID

from django.conf import settings

from backend.core.shared.domain_types import NotFoundError, PermissionDenied, Role
from backend.modules.recomendaciones.models import Evidencia
from backend.modules.usuarios.models import Usuario


class GetEvidenceFile:
    def execute(self, *, actor: Usuario, evidence_id: UUID) -> tuple[Path, str]:
        evidence = (
            Evidencia.objects.select_related("recomendacion__unidad_responsable")
            .filter(pk=evidence_id)
            .first()
        )
        if evidence is None:
            raise NotFoundError("La evidencia no existe.")

        same_unit = actor.unidad_org_id == evidence.recomendacion.unidad_responsable_id
        if actor.rol != Role.UAI.value and not (actor.rol == Role.EJECUTOR.value and same_unit):
            raise PermissionDenied("No tiene permisos para consultar esta evidencia.")
        if evidence.estado == Evidencia.Estado.ANULADA and actor.rol != Role.UAI.value:
            raise NotFoundError("La evidencia no existe.")

        path = Path(settings.MEDIA_ROOT) / "evidencias" / f"{evidence.id}.pdf"
        if not path.is_file():
            raise NotFoundError("El archivo de evidencia no está disponible.")
        return path, evidence.nombre_archivo
