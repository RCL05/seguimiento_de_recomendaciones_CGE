import csv
from io import StringIO

from django.http import HttpResponse, JsonResponse

from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.api.views import _user
from backend.core.shared.domain_types import Role
from backend.modules.recomendaciones.models import Recomendacion
from django.db.models import Count


def export_matriz_cge(request):
    if request.method != "POST":
        return JsonResponse(
            build_envelope(
                success=False,
                message="Método no permitido.",
                errors={"code": "METHOD_NOT_ALLOWED"},
                request_id=request_id_from(request),
            ),
            status=405,
        )
    user = _user(request)
    if user.role not in {Role.UAI, Role.RECTORADO, Role.CGE_AUDITOR}:
        return JsonResponse(
            build_envelope(
                success=False,
                message="No tiene permisos para exportar la matriz.",
                errors={"code": "PERMISSION_DENIED"},
                request_id=request_id_from(request),
            ),
            status=403,
        )
    output = StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["id", "informe", "numero", "unidad", "estado", "fecha_vencimiento"])
    for item in Recomendacion.objects.select_related("informe", "unidad_responsable").order_by("numero_recomendacion"):
        writer.writerow([
            item.id,
            item.informe.numero_informe,
            item.numero_recomendacion,
            item.unidad_responsable.codigo,
            item.estado,
            item.fecha_vencimiento_legal,
        ])
    response = HttpResponse(output.getvalue().encode("utf-8-sig"), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="matriz-cge.csv"'
    return response


def dashboard_summary(request):
    user = _user(request, Role.RECTORADO)
    if user.role not in {Role.RECTORADO, Role.UAI, Role.CGE_AUDITOR}:
        return JsonResponse(
            build_envelope(
                success=False,
                message="No tiene permisos para consultar el tablero.",
                errors={"code": "PERMISSION_DENIED"},
                request_id=request_id_from(request),
            ),
            status=403,
        )
    queryset = Recomendacion.objects.all()
    counts = {
        row["estado"]: row["total"]
        for row in queryset.values("estado").annotate(total=Count("id"))
    }
    total = sum(counts.values())
    completed = counts.get(Recomendacion.Estado.CUMPLIDA, 0)
    overdue = counts.get(Recomendacion.Estado.EN_MORA, 0)
    return JsonResponse(build_envelope(
        success=True,
        message="Resumen ejecutivo consultado",
        data={
            "total": total,
            "cumplimiento_porcentaje": round((completed / total) * 100, 2) if total else 0,
            "en_mora": overdue,
            "por_estado": counts,
        },
        request_id=request_id_from(request),
    ))
