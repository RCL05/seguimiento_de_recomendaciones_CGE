from django.urls import path

from . import views

app_name = "recomendaciones"

urlpatterns = [
    path("", views.recomendacion_lista, name="recomendacion_lista"),
    path("recomendaciones/nueva/", views.recomendacion_crear, name="recomendacion_crear"),
    path("recomendaciones/<int:pk>/", views.recomendacion_detalle, name="recomendacion_detalle"),
    path("recomendaciones/<int:pk>/editar/", views.recomendacion_editar, name="recomendacion_editar"),
    path("recomendaciones/<int:pk>/evidencias/", views.evidencia_cargar, name="evidencia_cargar"),
    path("evidencias/<int:pk>/anular/", views.evidencia_anular, name="evidencia_anular"),
]
