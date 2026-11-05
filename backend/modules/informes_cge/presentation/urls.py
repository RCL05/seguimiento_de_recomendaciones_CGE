from django.urls import path

from backend.modules.informes_cge.presentation.views import (
    InformeDetailView,
    InformeDocumentoView,
    InformeListCreateView,
)

urlpatterns = [
    path("informes", InformeListCreateView.as_view(), name="informes"),
    path("informes/<uuid:informe_id>", InformeDetailView.as_view(), name="informe-detalle"),
    path("informes/<uuid:informe_id>/documento", InformeDocumentoView.as_view(), name="informe-documento"),
]
