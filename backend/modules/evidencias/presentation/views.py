"""Capa API del módulo de evidencias: carga PDF, anulación lógica, descarga e integridad."""
from __future__ import annotations

from uuid import UUID

from django.http import FileResponse
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from backend.core.api.base import ApiView, FileDownloadView, ok
from backend.core.api.schema import envelope, errors
from backend.core.auth.permissions import IsAuthenticatedActor, require_roles
from backend.core.shared.domain_types import PayloadTooLarge, Role, ValidationError
from backend.modules.evidencias.application.anular_evidencia import AnularEvidencia
from backend.modules.evidencias.application.get_evidence_file import GetEvidenceFile
from backend.modules.evidencias.application.verify_integrity import VerificarIntegridadEvidencia
from backend.modules.evidencias.presentation.serializers import (
    AnulacionEvidenciaSerializer,
    ArchivoQuerySerializer,
    IntegridadSerializer,
)
from backend.modules.recomendaciones.application.upload_evidencia import MAX_SIZE_BYTES, UploadEvidencia
from backend.modules.recomendaciones.presentation.serializers import EvidenciaSerializer

CHUNK_SIZE = 64 * 1024


def _chunks(stream):
    if stream is None:
        return
    while True:
        chunk = stream.read(CHUNK_SIZE)
        if not chunk:
            return
        yield chunk


class EvidenciaUploadView(ApiView):
    permission_classes = [
        IsAuthenticatedActor,
        require_roles(Role.EJECUTOR, message="Solo el rol EJECUTOR puede cargar evidencias."),
    ]

    @extend_schema(
        tags=["Evidencias"],
        operation_id="cargarEvidencia",
        summary="Cargar una evidencia PDF (EJECUTOR, RF-008)",
        description=(
            "El cuerpo es el PDF binario (`Content-Type: application/pdf`, máximo 30 MB). "
            "Se calcula SHA-256 y la recomendación pasa a EN_VALIDACION."
        ),
        request={"application/pdf": OpenApiTypes.BINARY},
        parameters=[
            OpenApiParameter("X-Filename", str, OpenApiParameter.HEADER, required=True, description="Nombre del archivo .pdf"),
            OpenApiParameter(
                "X-Evidence-Type", str, OpenApiParameter.HEADER, enum=["BORRADOR", "FINAL"], description="Por defecto BORRADOR"
            ),
        ],
        responses={201: envelope("Evidencia", EvidenciaSerializer), **errors(400, 401, 403, 404, 409, 413)},
    )
    def post(self, request, recommendation_id: UUID):
        content_length = request.headers.get("Content-Length")
        if content_length is not None:
            try:
                size = int(content_length)
            except ValueError as error:
                raise ValidationError("Content-Length inválido.") from error
            if size < 0:
                raise ValidationError("Content-Length inválido.")
            if size > MAX_SIZE_BYTES:
                raise PayloadTooLarge("El PDF supera el tamaño máximo permitido.")
        evidence = UploadEvidencia().execute(
            actor=self.actor,
            request_id=self.request_id,
            recommendation_id=recommendation_id,
            filename=request.headers.get("X-Filename", "evidence.pdf"),
            content=_chunks(request.stream),
            evidence_type=request.headers.get("X-Evidence-Type", "BORRADOR").upper(),
            ip_address=self.client_ip,
        )
        return ok(
            request,
            EvidenciaSerializer(evidence).data,
            "Evidencia cargada",
            status=201,
            location=reverse("evidencia-archivo", args=[evidence.id]),
        )


class EvidenciaDetailView(ApiView):
    permission_classes = [
        IsAuthenticatedActor,
        require_roles(Role.UAI, message="Solo el rol UAI puede anular evidencias."),
    ]

    @extend_schema(
        tags=["Evidencias"],
        operation_id="anularEvidencia",
        summary="Anular lógicamente una evidencia (UAI)",
        description="Modificación parcial del estado: la evidencia y su historial se conservan (CA-07.3).",
        request=AnulacionEvidenciaSerializer,
        responses={200: envelope("EvidenciaAnulada", EvidenciaSerializer), **errors(400, 401, 403, 404, 409)},
    )
    def patch(self, request, evidence_id: UUID):
        payload = AnulacionEvidenciaSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        evidence = AnularEvidencia().execute(
            actor=self.actor,
            request_id=self.request_id,
            evidence_id=evidence_id,
            reason=payload.validated_data["motivo"],
            ip_address=self.client_ip,
        )
        return ok(request, EvidenciaSerializer(evidence).data, "Evidencia anulada")


class EvidenciaArchivoView(FileDownloadView):
    @extend_schema(
        tags=["Evidencias"],
        operation_id="descargarEvidencia",
        summary="Abrir o descargar el PDF de una evidencia",
        parameters=[ArchivoQuerySerializer],
        responses={
            (200, "application/pdf"): OpenApiResponse(OpenApiTypes.BINARY, description="Contenido PDF."),
            **errors(400, 401, 403, 404),
        },
    )
    def get(self, request, evidence_id: UUID):
        query = ArchivoQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        path, filename = GetEvidenceFile().execute(actor=self.actor, evidence_id=evidence_id)
        return FileResponse(
            path.open("rb"),
            as_attachment=query.validated_data["disposition"] == "attachment",
            filename=filename,
            content_type="application/pdf",
        )


class EvidenciaIntegridadView(ApiView):
    @extend_schema(
        tags=["Evidencias"],
        operation_id="verificarIntegridadEvidencia",
        summary="Verificar el SHA-256 del archivo almacenado (UAI, auditor CGE)",
        responses={200: envelope("Integridad", IntegridadSerializer), **errors(401, 403, 404)},
    )
    def get(self, request, evidence_id: UUID):
        result = VerificarIntegridadEvidencia().execute(
            actor=self.actor,
            evidence_id=evidence_id,
            request_id=self.request_id,
        )
        message = "La evidencia es íntegra." if result["integra"] else "ALERTA: el archivo no coincide con el hash registrado."
        return ok(request, IntegridadSerializer(result).data, message)
