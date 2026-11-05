from django.urls import path

from backend.modules.reportes.presentation.views import AuditoriaView, MatrizCgeView, TableroView

urlpatterns = [
    path("reportes/tablero", TableroView.as_view(), name="tablero"),
    path("reportes/matriz-cge", MatrizCgeView.as_view(), name="matriz-cge"),
    path("auditoria", AuditoriaView.as_view(), name="auditoria"),
]
