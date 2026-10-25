from __future__ import annotations

import csv
from io import StringIO

from backend.modules.recomendaciones.models import Recomendacion


def export_matriz_cge_csv():
    output = StringIO()
    writer = csv.writer(output, delimiter=",", lineterminator="\n")
    writer.writerow([
        "numero_informe",
        "numero_recomendacion",
        "unidad_responsable",
        "estado",
        "prioridad",
        "fecha_vencimiento_legal",
        "plazo_legal_dias",
    ])
    for rec in Recomendacion.objects.select_related("informe", "unidad_responsable").all():
        writer.writerow([
            rec.informe.numero_informe,
            rec.numero_recomendacion,
            rec.unidad_responsable.codigo,
            rec.estado,
            rec.prioridad,
            rec.fecha_vencimiento_legal.isoformat() if rec.fecha_vencimiento_legal else "",
            rec.plazo_legal_dias,
        ])
    content = output.getvalue()
    return content.encode("utf-8")
