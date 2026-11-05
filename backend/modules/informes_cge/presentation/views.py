"""Capa API del módulo de informes CGE."""
from __future__ import annotations

from uuid import UUID

from django.urls import reverse
from drf_spectacular.utils import extend_schema

from backend.core.api.base import ApiView, ok, page_meta
from backend.core.api.schema import envelope, errors
from backend.core.auth.permissions import IsAuthenticatedActor, require_roles
from backend.core.shared.domain_types import PayloadTooLarge, Role
from backend.modules.informes_cge.application.consultar_informes import ListarInformes, ObtenerInforme
from backend.modules.informes_cge.application.register_informe import RegisterInforme
from backend.modules.informes_cge.presentation.serializers import (
    InformeCreateSerializer,
    InformeSerializer,
    PaginacionQuerySerializer,
)
from backend.modules.recomendaciones.application.upload_evidencia import MAX_SIZE_BYTES

SOLO_UAI = require_roles(Role.UAI, message="Solo el rol UAI puede registrar informes.")


class InformeListCreateView(ApiView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedActor(), SOLO_UAI()]
        return super().get_permissions()

    @extend_schema(
        tags=["Informes CGE"],
        operation_id="listarInformes",
        summary="Consultar informes de examen especial (UAI, Rectorado, auditor CGE)",
        parameters=[PaginacionQuerySerializer],
        responses={200: envelope("Informes", InformeSerializer, many=True), **errors(400, 401, 403)},
    )
    def get(self, request):
        query = PaginacionQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        page = ListarInformes().execute(actor=self.actor, **query.validated_data)
        return ok(
            request,
            InformeSerializer(page.object_list, many=True).data,
            "Informes consultados",
            pagination=page_meta(page),
        )

    @extend_schema(
        tags=["Informes CGE"],
        operation_id="registrarInforme",
        summary="Registrar un informe CGE con su documento oficial (UAI, RF-005)",
        request={
            "application/json": InformeCreateSerializer,
            "multipart/form-data": InformeCreateSerializer,
        },
        responses={201: envelope("Informe", InformeSerializer), **errors(400, 401, 403, 409, 413)},
    )
    def post(self, request):
        archivo = request.FILES.get("pdf_informe")
        if archivo is not None and archivo.size > MAX_SIZE_BYTES:
            raise PayloadTooLarge("El PDF supera el tamaño máximo permitido.")
        payload = InformeCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data
        informe = RegisterInforme().execute(
            number=data["numero_informe"],
            audited_period=data["periodo_auditado"],
            notification_date=data["fecha_notificacion"],
            document_url=data.get("pdf_informe_url", ""),
            document_file=data.get("pdf_informe"),
            creator=self.actor,
            request_id=self.request_id,
            ip_address=self.client_ip,
        )
        return ok(
            request,
            InformeSerializer(informe).data,
            "Informe CGE registrado",
            status=201,
            location=reverse("informe-detalle", args=[informe.id]),
        )


class InformeDetailView(ApiView):
    @extend_schema(
        tags=["Informes CGE"],
        operation_id="consultarInforme",
        summary="Consultar un informe CGE",
        responses={200: envelope("InformeDetalle", InformeSerializer), **errors(401, 403, 404)},
    )
    def get(self, request, informe_id: UUID):
        informe = ObtenerInforme().execute(actor=self.actor, informe_id=informe_id)
        return ok(request, InformeSerializer(informe).data, "Informe consultado")
