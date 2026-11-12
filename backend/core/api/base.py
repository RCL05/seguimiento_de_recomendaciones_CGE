"""Base común de la capa API (presentación) construida sobre Django REST Framework.

Responsabilidad: traducir HTTP <-> casos de uso. No contiene reglas de negocio.
"""
from __future__ import annotations

from typing import Any

from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.core.api import schema as _schema  # noqa: F401  (registra JWTBearerScheme)
from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.auth.authentication import JWTBearerAuthentication
from backend.core.auth.permissions import IsAuthenticatedActor


class ApiView(APIView):
    # Vista base: JWT Bearer obligatorio y 405 evaluado antes de autenticar.
    # (Comentario y no docstring: drf-spectacular usaría la docstring heredada como
    # descripción de cada operación del contrato OpenAPI.)

    authentication_classes = [JWTBearerAuthentication]
    permission_classes = [IsAuthenticatedActor]

    def initial(self, request, *args, **kwargs):
        method = request.method.lower()
        if method not in self.http_method_names or not hasattr(self, method):
            # RFC 9110 §15.5.6: el método no existe para el recurso, sin importar quién pregunta.
            raise MethodNotAllowed(request.method)
        super().initial(request, *args, **kwargs)

    @property
    def actor(self):
        return self.request.user

    @property
    def request_id(self):
        return request_id_from(self.request)

    @property
    def client_ip(self) -> str | None:
        return self.request.META.get("REMOTE_ADDR")


class FileDownloadView(ApiView):
    # Vista que entrega un archivo (PDF o CSV) con HttpResponse/FileResponse, fuera del
    # renderizado de DRF. DRF solo negocia JSON y, sin esto, un cliente que envía
    # `Accept: application/pdf` o `Accept: text/csv` recibiría 406 antes de llegar a la
    # vista. Con force=True la negociación no falla: el archivo se entrega igual y los
    # errores (401, 403, 404) siguen saliendo en la envoltura JSON.

    def perform_content_negotiation(self, request, force=False):
        return super().perform_content_negotiation(request, force=True)


def ok(
    request,
    data: Any,
    message: str,
    *,
    status: int = 200,
    location: str | None = None,
    pagination: dict | None = None,
) -> Response:
    """Respuesta exitosa con el contrato universal (`success`, `message`, `data`, `errors`, `meta`)."""
    response = Response(
        build_envelope(
            success=True,
            message=message,
            data=data,
            request_id=request_id_from(request),
            pagination=pagination,
        ),
        status=status,
    )
    if location:
        # RFC 9110 §10.2.2: en 201 Created, Location identifica el recurso creado.
        response["Location"] = location
    return response


def page_meta(page) -> dict:
    """Metadatos de paginación a partir de un `django.core.paginator.Page`."""
    return {
        "page": page.number,
        "page_size": page.paginator.per_page,
        "total": page.paginator.count,
        "total_pages": page.paginator.num_pages,
        "has_next": page.has_next(),
        "has_previous": page.has_previous(),
    }
