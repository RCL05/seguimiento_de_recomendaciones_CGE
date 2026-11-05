"""Rutas de SITRA-CGE.

Cada módulo expone sus recursos REST versionados bajo /api/v1/ desde su capa
`presentation/urls.py`. Las rutas nombran recursos (sustantivos) y el método HTTP
expresa la operación (Semana 3: preferir recursos frente a acciones arbitrarias).
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from backend.core.api.health import HealthView
from backend.core.api.middleware import handler404 as api_handler404
from backend.core.api.middleware import handler500 as api_handler500
from backend.core.web.views import dashboard

API_V1 = "api/v1/"

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path(API_V1, include("backend.modules.usuarios.presentation.urls")),
    path(API_V1, include("backend.modules.informes_cge.presentation.urls")),
    path(API_V1, include("backend.modules.recomendaciones.presentation.urls")),
    path(API_V1, include("backend.modules.evidencias.presentation.urls")),
    path(API_V1, include("backend.modules.reportes.presentation.urls")),
    path(API_V1, include("backend.modules.notificaciones.presentation.urls")),
    # Contrato OpenAPI generado desde el código y Swagger UI para probar los endpoints.
    path("api/schema/", SpectacularAPIView.as_view(), name="openapi-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="openapi-schema"), name="swagger-ui"),
    path("", dashboard, name="dashboard"),
]

handler404 = api_handler404
handler500 = api_handler500

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
