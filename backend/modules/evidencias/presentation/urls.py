from django.urls import path

from backend.modules.evidencias.presentation.views import (
    EvidenciaArchivoView,
    EvidenciaDetailView,
    EvidenciaIntegridadView,
    EvidenciaUploadView,
)

urlpatterns = [
    path(
        "recomendaciones/<uuid:recommendation_id>/evidencias",
        EvidenciaUploadView.as_view(),
        name="evidencias",
    ),
    path("evidencias/<uuid:evidence_id>", EvidenciaDetailView.as_view(), name="evidencia-detalle"),
    path("evidencias/<uuid:evidence_id>/archivo", EvidenciaArchivoView.as_view(), name="evidencia-archivo"),
    path(
        "evidencias/<uuid:evidence_id>/integridad",
        EvidenciaIntegridadView.as_view(),
        name="evidencia-integridad",
    ),
]
