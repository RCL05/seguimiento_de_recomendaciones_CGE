from django.urls import path

from backend.modules.reportes.presentation.views import AuditoriaView, KpisView, MatrizCgeView, TableroView

urlpatterns = [
    path("dashboard/kpis", KpisView.as_view(), name="dashboard-kpis"),
    path("reportes/tablero", TableroView.as_view(), name="tablero"),
    path("reportes/matriz-cge", MatrizCgeView.as_view(), name="matriz-cge"),
    path("auditoria", AuditoriaView.as_view(), name="auditoria"),
]
