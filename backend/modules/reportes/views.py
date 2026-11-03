import csv
from io import StringIO

from django.http import HttpResponse, JsonResponse

from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.api.views import _persistent_user, _user
from backend.core.audit.repository import query_audit_log
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
    """Tablero ejecutivo con semáforo de riesgo (RF-013).

    Accesible por RECTORADO, UAI y CGE_AUDITOR.
    """
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
    in_revision = counts.get(Recomendacion.Estado.EN_REVISION_INTERNA, 0)
    pct = round((completed / total) * 100, 2) if total else 0

    # Semáforo de riesgo institucional
    if pct >= 75:
        semaforo = "VERDE"
    elif pct >= 40:
        semaforo = "AMARILLO"
    else:
        semaforo = "ROJO"

    return JsonResponse(build_envelope(
        success=True,
        message="Resumen ejecutivo consultado",
        data={
            "total": total,
            "cumplimiento_porcentaje": pct,
            "semaforo_riesgo": semaforo,
            "en_mora": overdue,
            "en_revision_interna": in_revision,
            "por_estado": counts,
        },
        request_id=request_id_from(request),
    ))


def audit_log_list(request):
    """Consulta del historial de auditoría (RF-018, US5/AC1).

    Accesible solo por UAI y CGE_AUDITOR.
    Soporta filtros: entity, entity_id, limit.
    """
    user, _ = _persistent_user(request)
    if user.role not in {Role.UAI, Role.CGE_AUDITOR}:
        return JsonResponse(
            build_envelope(
                success=False,
                message="No tiene permisos para consultar la auditoría.",
                errors={"code": "PERMISSION_DENIED"},
                request_id=request_id_from(request),
            ),
            status=403,
        )

    entity = request.GET.get("entity")
    entity_id = request.GET.get("entity_id")
    limit = min(int(request.GET.get("limit", 100)), 500)

    logs = query_audit_log(
        entity=entity or None,
        entity_id=entity_id or None,
        limit=limit,
    )

    data = [
        {
            "id": log.id,
            "request_id": str(log.request_id),
            "timestamp_utc": log.timestamp_utc.isoformat(),
            "usuario": log.usuario.correo_institucional if log.usuario else None,
            "modulo": log.modulo,
            "accion": log.accion,
            "entidad": log.entidad,
            "entidad_id": str(log.entidad_id) if log.entidad_id else None,
            "estado_anterior": log.estado_anterior,
            "estado_nuevo": log.estado_nuevo,
            "resultado": log.resultado,
            "ip_origen": log.ip_origen,
        }
        for log in logs
    ]
    return JsonResponse(build_envelope(
        success=True,
        message="Historial de auditoría consultado",
        data=data,
        request_id=request_id_from(request),
    ))
