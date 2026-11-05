"""Caso de uso: exportar la matriz institucional de cumplimiento en CSV UTF-8 (RF-014)."""
from __future__ import annotations

import csv
from io import StringIO

from backend.core.shared.domain_types import PermissionDenied
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario

ROLES_MATRIZ = {Usuario.Rol.UAI, Usuario.Rol.RECTORADO, Usuario.Rol.CGE_AUDITOR}

COLUMNAS = [
    "numero_informe",
    "numero_recomendacion",
    "descripcion",
    "unidad_responsable",
    "prioridad",
    "estado",
    "plazo_legal_dias",
    "fecha_vencimiento_legal",
]


def export_matriz_cge_csv(*, actor: Usuario) -> bytes:
    if actor.rol not in ROLES_MATRIZ:
        raise PermissionDenied("No tiene permisos para exportar la matriz.")
    output = StringIO()
    writer = csv.writer(output, delimiter=",", lineterminator="\n")
    writer.writerow(COLUMNAS)
    recomendaciones = Recomendacion.objects.select_related("informe", "unidad_responsable").order_by(
        "informe__numero_informe", "numero_recomendacion"
    )
    for rec in recomendaciones:
        writer.writerow([
            rec.informe.numero_informe,
            rec.numero_recomendacion,
            rec.descripcion,
            rec.unidad_responsable.codigo,
            rec.prioridad,
            rec.estado,
            rec.plazo_legal_dias,
            rec.fecha_vencimiento_legal.isoformat() if rec.fecha_vencimiento_legal else "",
        ])
    # BOM UTF-8 para que hojas de cálculo reconozcan la codificación.
    return output.getvalue().encode("utf-8-sig")
