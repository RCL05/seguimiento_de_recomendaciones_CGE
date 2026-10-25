from django.urls import path

from backend.core.api.views import (
    health,
    login_sso,
    report_create,
    recommendation_detail,
    recommendation_evidence,
    recommendation_list,
    recommendation_review,
    recommendation_plan,
)
from backend.core.web.views import dashboard
from backend.modules.reportes.views import dashboard_summary, export_matriz_cge
from backend.modules.notificaciones.views import notification_inbox

urlpatterns = [
    path("health/", health, name="health"),
    path("api/v1/auth/login-sso", login_sso, name="login-sso"),
    path("api/v1/recomendaciones", recommendation_list, name="recommendation-list"),
    path("api/v1/informes", report_create, name="report-create"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>", recommendation_detail, name="recommendation-detail"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>/plan-accion", recommendation_plan, name="recommendation-plan"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>/evidencias", recommendation_evidence, name="recommendation-evidence"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>/dictamen", recommendation_review, name="recommendation-review"),
    path("api/v1/reportes/matriz-cge", export_matriz_cge, name="export-matriz-cge"),
    path("api/v1/reportes/tablero", dashboard_summary, name="dashboard-summary"),
    path("api/v1/notificaciones", notification_inbox, name="notification-inbox"),
    path("", dashboard, name="dashboard"),
]
