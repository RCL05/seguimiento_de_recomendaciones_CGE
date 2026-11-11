"""Capa API del módulo de recomendaciones: registro, consulta, plan de acción y dictamen UAI."""
from __future__ import annotations

from uuid import UUID

from django.urls import reverse
from drf_spectacular.utils import extend_schema

from backend.core.api.base import ApiView, ok, page_meta
from backend.core.api.schema import envelope, errors
from backend.core.auth.permissions import IsAuthenticatedActor, require_roles
from backend.core.shared.domain_types import Role
from backend.modules.recomendaciones.application.create_plan_accion import CreatePlanAccion
from backend.modules.recomendaciones.application.create_recomendacion import CreateRecomendacion
from backend.modules.recomendaciones.application.get_recomendacion import GetRecomendacion
from backend.modules.recomendaciones.application.issue_dictamen import IssueDictamen
from backend.modules.recomendaciones.application.list_recomendaciones import ListRecomendaciones
from backend.modules.recomendaciones.application.reabrir_recomendacion import ReabrirRecomendacion
from backend.modules.recomendaciones.application.reasignar_recomendacion import (
    ReasignarRecomendacion,
)
from backend.modules.recomendaciones.presentation.serializers import (
    DictamenCreateSerializer,
    DictamenSerializer,
    HitoCreateSerializer,
    HitoSerializer,
    RecomendacionCreateSerializer,
    RecomendacionDetalleSerializer,
    RecomendacionPatchSerializer,
    RecomendacionQuerySerializer,
    RecomendacionSerializer,
)

SOLO_UAI = require_roles(Role.UAI, message="Solo el rol UAI puede realizar esta operación.")
SOLO_EJECUTOR = require_roles(Role.EJECUTOR, message="Solo el rol EJECUTOR puede registrar hitos del plan.")


class RecomendacionListCreateView(ApiView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedActor(), SOLO_UAI()]
        return super().get_permissions()

    @extend_schema(
        tags=["Recomendaciones"],
        operation_id="listarRecomendaciones",
        summary="Consultar recomendaciones visibles para el usuario (paginado y filtrable)",
        description="El ejecutor solo ve las recomendaciones de su unidad (RF-019).",
        parameters=[RecomendacionQuerySerializer],
        responses={200: envelope("Recomendaciones", RecomendacionSerializer, many=True), **errors(400, 401, 403)},
    )
    def get(self, request):
        query = RecomendacionQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        filters = query.validated_data
        page = ListRecomendaciones().execute(
            actor=self.actor,
            page=filters["page"],
            page_size=filters["page_size"],
            state=filters.get("state"),
            unit_code=filters.get("unit_id"),
            priority=filters.get("priority"),
            due_date=_iso(filters.get("due_date")),
            due_before=_iso(filters.get("due_before")),
            due_after=_iso(filters.get("due_after")),
            overdue=filters.get("vencida"),
        )
        return ok(
            request,
            RecomendacionSerializer(page.object_list, many=True).data,
            "Recomendaciones consultadas",
            pagination=page_meta(page),
        )

    @extend_schema(
        tags=["Recomendaciones"],
        operation_id="registrarRecomendacion",
        summary="Registrar y asignar una recomendación (UAI, RF-006)",
        description="La recomendación se crea en estado PENDIENTE.",
        request=RecomendacionCreateSerializer,
        responses={201: envelope("Recomendacion", RecomendacionSerializer), **errors(400, 401, 403, 409)},
    )
    def post(self, request):
        payload = RecomendacionCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data
        recommendation = CreateRecomendacion().execute(
            actor=self.actor,
            request_id=self.request_id,
            report_id=data["report_id"],
            number=data["number"],
            description=data["description"],
            unit_id=data["unit_id"],
            legal_days=data["legal_days"],
            due_date=data["due_date"],
            priority=data["priority"],
            ip_address=self.client_ip,
        )
        return ok(
            request,
            RecomendacionSerializer(recommendation).data,
            "Recomendación creada",
            status=201,
            location=reverse("recomendacion-detalle", args=[recommendation.id]),
        )


class RecomendacionDetailView(ApiView):
    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAuthenticatedActor(), SOLO_UAI()]
        return super().get_permissions()

    @extend_schema(
        tags=["Recomendaciones"],
        operation_id="modificarRecomendacion",
        summary="Reabrir o reasignar una recomendación (UAI, RF-023 y RF-003)",
        description=(
            "Modificación parcial con motivo obligatorio. Se envía `estado: REABIERTA` para reabrir "
            "una recomendación cumplida (solo CUMPLIDA → REABIERTA), o `unit_id` para reasignarla a "
            "otra unidad. La reasignación conserva el estado y registra en auditoría la unidad "
            "anterior, la nueva y el motivo."
        ),
        request=RecomendacionPatchSerializer,
        responses={200: envelope("RecomendacionModificada", RecomendacionSerializer), **errors(400, 401, 403, 404, 409)},
    )
    def patch(self, request, recommendation_id: UUID):
        payload = RecomendacionPatchSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data
        if "unit_id" in data:
            recommendation = ReasignarRecomendacion().execute(
                actor=self.actor,
                request_id=self.request_id,
                recommendation_id=recommendation_id,
                unit_id=data["unit_id"],
                reason=data["motivo"],
                ip_address=self.client_ip,
            )
            message = "Recomendación reasignada"
        else:
            recommendation = ReabrirRecomendacion().execute(
                actor=self.actor,
                request_id=self.request_id,
                recommendation_id=recommendation_id,
                reason=data["motivo"],
                ip_address=self.client_ip,
            )
            message = "Recomendación reabierta"
        return ok(request, RecomendacionSerializer(recommendation).data, message)

    @extend_schema(
        tags=["Recomendaciones"],
        operation_id="consultarRecomendacion",
        summary="Consultar una recomendación con sus evidencias",
        description="Una recomendación de otra unidad responde 404 sin revelar su existencia (RF-019).",
        responses={200: envelope("RecomendacionDetalle", RecomendacionDetalleSerializer), **errors(401, 403, 404)},
    )
    def get(self, request, recommendation_id: UUID):
        recommendation = GetRecomendacion().execute(
            actor=self.actor,
            recommendation_id=recommendation_id,
            request_id=self.request_id,
            ip_address=self.client_ip,
        )
        return ok(request, RecomendacionDetalleSerializer(recommendation).data, "Recomendación consultada")


class PlanAccionView(ApiView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedActor(), SOLO_EJECUTOR()]
        return super().get_permissions()

    @extend_schema(
        tags=["Plan de acción"],
        operation_id="listarHitos",
        summary="Consultar los hitos del plan de acción",
        responses={200: envelope("Hitos", HitoSerializer, many=True), **errors(401, 403, 404)},
    )
    def get(self, request, recommendation_id: UUID):
        recommendation = GetRecomendacion().execute(
            actor=self.actor,
            recommendation_id=recommendation_id,
            request_id=self.request_id,
            ip_address=self.client_ip,
        )
        hitos = recommendation.planes.order_by("fecha_compromiso")
        return ok(request, HitoSerializer(hitos, many=True).data, "Plan de acción consultado")

    @extend_schema(
        tags=["Plan de acción"],
        operation_id="registrarHito",
        summary="Registrar un hito del plan de acción (EJECUTOR, RF-007)",
        description=(
            "El primer hito inicia la ejecución: PENDIENTE/REABIERTA → EN_PROCESO. Dentro del plazo, "
            "la fecha no excede el plazo legal; con el plazo vencido, debe ser hoy o posterior."
        ),
        request=HitoCreateSerializer,
        responses={201: envelope("Hito", HitoSerializer), **errors(400, 401, 403, 404, 409)},
    )
    def post(self, request, recommendation_id: UUID):
        payload = HitoCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        hito = CreatePlanAccion().execute(
            actor=self.actor,
            request_id=self.request_id,
            recommendation_id=recommendation_id,
            description=payload.validated_data["descripcion_hito"],
            commitment_date=payload.validated_data["fecha_compromiso"],
            ip_address=self.client_ip,
        )
        return ok(
            request,
            HitoSerializer(hito).data,
            "Hito del plan de acción registrado",
            status=201,
            location=reverse("plan-accion", args=[recommendation_id]),
        )


class DictamenView(ApiView):
    permission_classes = [IsAuthenticatedActor, require_roles(Role.UAI, message="Solo el rol UAI puede emitir dictámenes.")]

    @extend_schema(
        tags=["Dictamen UAI"],
        operation_id="emitirDictamen",
        summary="Emitir el dictamen UAI sobre una evidencia (RF-009, RF-010)",
        description=(
            "Aprobado → CUMPLIDA (requiere revisión interna y PDF validado). "
            "Rechazado → EN_PROCESO, con observaciones obligatorias."
        ),
        request=DictamenCreateSerializer,
        responses={201: envelope("Dictamen", DictamenSerializer), **errors(400, 401, 403, 404, 409)},
    )
    def post(self, request, recommendation_id: UUID):
        payload = DictamenCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        dictamen = IssueDictamen().execute(
            actor=self.actor,
            request_id=self.request_id,
            recommendation_id=recommendation_id,
            evidence_id=payload.validated_data["evidence_id"],
            approved=payload.validated_data["approved"],
            observations=payload.validated_data["observaciones"],
            ip_address=self.client_ip,
        )
        return ok(request, DictamenSerializer(dictamen).data, "Dictamen registrado", status=201)


def _iso(value):
    return value.isoformat() if value else None
