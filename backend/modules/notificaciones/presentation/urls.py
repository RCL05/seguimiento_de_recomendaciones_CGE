from django.urls import path

from backend.modules.notificaciones.presentation.views import (
    BandejaView,
    ConfiguracionView,
    PreferenciasView,
)

urlpatterns = [
    path("notificaciones", BandejaView.as_view(), name="notificaciones"),
    path("notificaciones/preferencias", PreferenciasView.as_view(), name="notificaciones-preferencias"),
    path("notificaciones/configuracion", ConfiguracionView.as_view(), name="notificaciones-configuracion"),
]
