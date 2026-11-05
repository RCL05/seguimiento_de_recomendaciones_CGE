from django.conf import settings
from django.conf.urls.static import static
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
    evidence_annul,
    evidence_file,
    units_list,
)
from backend.core.api.middleware import handler404 as api_handler404
from backend.core.api.middleware import handler500 as api_handler500
from backend.core.web.views import dashboard
from backend.modules.reportes.views import dashboard_summary, export_matriz_cge, audit_log_list
from backend.modules.notificaciones.presentation.preferences_views import (
    notification_preferences,
    notification_settings,
)
from backend.modules.notificaciones.views import notification_inbox, run_jobs

urlpatterns = [
    # Salud del servicio
    path("health/", health, name="health"),

    # Autenticación
    path("api/v1/auth/login-sso", login_sso, name="login-sso"),
    path("api/v1/unidades", units_list, name="units-list"),

    # Informes CGE
    path("api/v1/informes", report_create, name="report-create"),

    # Recomendaciones
    path("api/v1/recomendaciones", recommendation_list, name="recommendation-list"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>", recommendation_detail, name="recommendation-detail"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>/plan-accion", recommendation_plan, name="recommendation-plan"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>/evidencias", recommendation_evidence, name="recommendation-evidence"),
    path("api/v1/evidencias/<uuid:evidence_id>", evidence_annul, name="evidence-annul"),
    path("api/v1/evidencias/<uuid:evidence_id>/archivo", evidence_file, name="evidence-file"),
    path("api/v1/recomendaciones/<uuid:recommendation_id>/dictamen", recommendation_review, name="recommendation-review"),

    # Reportes y tablero
    path("api/v1/reportes/matriz-cge", export_matriz_cge, name="export-matriz-cge"),
    path("api/v1/reportes/tablero", dashboard_summary, name="dashboard-summary"),

    # Auditoría
    path("api/v1/auditoria", audit_log_list, name="audit-log-list"),

    # Notificaciones
    path("api/v1/notificaciones", notification_inbox, name="notification-inbox"),
    path(
        "api/v1/notificaciones/preferencias",
        notification_preferences,
        name="notification-preferences",
    ),
    path(
        "api/v1/notificaciones/configuracion",
        notification_settings,
        name="notification-settings",
    ),

    # Jobs internos (solo uso interno / DTI)
    path("api/v1/jobs/evaluar-plazos", run_jobs, name="run-jobs"),

    # Web
    path("", dashboard, name="dashboard"),
]

handler404 = api_handler404
handler500 = api_handler500

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
