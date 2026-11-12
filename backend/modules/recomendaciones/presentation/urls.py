from django.urls import path

from backend.modules.recomendaciones.presentation.views import (
    DictamenDetailView,
    DictamenView,
    PlanAccionView,
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
        "recomendaciones/<uuid:recommendation_id>/hitos",
        PlanAccionView.as_view(),
        name="hitos",
    ),
    path(
        "recomendaciones/<uuid:recommendation_id>/dictamenes",
        DictamenView.as_view(),
        name="dictamenes",
    ),
    path(
        "recomendaciones/<uuid:recommendation_id>/dictamenes/<uuid:dictamen_id>",
        DictamenDetailView.as_view(),
        name="dictamen-detalle",
    ),
]
