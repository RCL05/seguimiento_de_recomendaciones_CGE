"""Capa API del módulo de reportes: tablero ejecutivo, matriz CGE y consulta de auditoría."""
from __future__ import annotations

from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers

from backend.core.api.base import ApiView, ok
from backend.core.api.schema import envelope, errors
from backend.core.audit.repository import query_audit_log
from backend.core.auth.permissions import IsAuthenticatedActor, require_roles
from backend.core.shared.domain_types import Role
from backend.modules.reportes.application.export_matriz import export_matriz_cge_csv
from backend.modules.reportes.application.get_dashboard import get_dashboard
from backend.modules.reportes.application.get_kpis import get_kpis
from backend.modules.reportes.presentation.serializers import (
    AuditLogSerializer,
    AuditoriaQuerySerializer,
    TableroSerializer,
)


class KpisSerializer(serializers.Serializer):
    total_recomendaciones = serializers.IntegerField()
    recomendaciones_por_estado = serializers.DictField(child=serializers.IntegerField())
    tasa_cumplimiento_porcentaje = serializers.FloatField()
    recomendaciones_vencidas_o_en_mora = serializers.IntegerField()
    total_informes_cge = serializers.IntegerField()


class KpisView(ApiView):
    @extend_schema(
        tags=["Dashboard"],
        operation_id="consultarKpisDashboard",
        summary="Consultar indicadores clave del sistema",
        responses={200: envelope("KpisDashboard", KpisSerializer), **errors(401, 403, 500)},
    )
    def get(self, request):
        data = get_kpis()
        return ok(request, KpisSerializer(data).data, "Indicadores del dashboard consultados")


class TableroView(ApiView):
    @extend_schema(
        tags=["Reportes"],
        operation_id="consultarTablero",
        summary="Tablero ejecutivo: semáforo, cumplimiento y unidades en mora (RF-013)",
        responses={200: envelope("Tablero", TableroSerializer), **errors(401, 403)},
    )
    def get(self, request):
        data = get_dashboard(actor=self.actor)
        return ok(request, TableroSerializer(data).data, "Resumen ejecutivo consultado")


class MatrizCgeView(ApiView):
    @extend_schema(
        tags=["Reportes"],
        operation_id="exportarMatrizCge",
        summary="Exportar la matriz institucional de cumplimiento (CSV UTF-8, RF-014)",
        description="Descarga binaria: no usa la envoltura JSON (excepción del contrato universal).",
        responses={
            (200, "text/csv"): OpenApiResponse(OpenApiTypes.BINARY, description="Matriz CSV con BOM UTF-8."),
            **errors(401, 403),
        },
    )
    def get(self, request):
        content = export_matriz_cge_csv(actor=self.actor)
        response = HttpResponse(content, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="matriz-cge.csv"'
        return response


class AuditoriaView(ApiView):
    permission_classes = [
        IsAuthenticatedActor,
        require_roles(Role.UAI, Role.CGE_AUDITOR, message="No tiene permisos para consultar la auditoría."),
    ]

    @extend_schema(
        tags=["Auditoría"],
        operation_id="consultarAuditoria",
        summary="Consultar el historial inmutable de auditoría (UAI, auditor CGE, RF-018)",
        parameters=[AuditoriaQuerySerializer],
        responses={200: envelope("Auditoria", AuditLogSerializer, many=True), **errors(400, 401, 403)},
    )
    def get(self, request):
        query = AuditoriaQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        logs = query_audit_log(
            entity=query.validated_data.get("entity"),
            entity_id=query.validated_data.get("entity_id"),
            limit=query.validated_data["limit"],
        )
        return ok(request, AuditLogSerializer(logs, many=True).data, "Historial de auditoría consultado")
