from django.urls import path

from backend.modules.informes_cge.presentation.views import InformeDetailView, InformeListCreateView

urlpatterns = [
    path("informes", InformeListCreateView.as_view(), name="informes"),
    path("informes/<uuid:informe_id>", InformeDetailView.as_view(), name="informe-detalle"),
]
