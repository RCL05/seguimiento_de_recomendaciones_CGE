from django.urls import path

from backend.modules.recomendaciones.presentation.views import (
    DictamenView,
    PlanAccionView,
    ReasignacionView,
    RecomendacionDetailView,
    RecomendacionListCreateView,
)

urlpatterns = [
    path("recomendaciones", RecomendacionListCreateView.as_view(), name="recomendaciones"),
    path(
        "recomendaciones/<uuid:recommendation_id>",
        RecomendacionDetailView.as_view(),
        name="recomendacion-detalle",
    ),
    path(
        "recomendaciones/<uuid:recommendation_id>/reasignacion",
        ReasignacionView.as_view(),
        name="reasignacion",
    ),
    path(
        "recomendaciones/<uuid:recommendation_id>/plan-accion",
        PlanAccionView.as_view(),
        name="plan-accion",
    ),
    path(
        "recomendaciones/<uuid:recommendation_id>/dictamenes",
        DictamenView.as_view(),
        name="dictamenes",
    ),
]
