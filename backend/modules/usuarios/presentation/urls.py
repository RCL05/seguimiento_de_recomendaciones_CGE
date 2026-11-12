from django.urls import path

from backend.modules.usuarios.presentation.views import (
    LoginSsoView,
    UnidadListCreateView,
    UsuarioDetailView,
    UsuarioListView,
)

urlpatterns = [
    path("sesiones", LoginSsoView.as_view(), name="sesiones"),
    path("unidades", UnidadListCreateView.as_view(), name="unidades"),
    path("usuarios", UsuarioListView.as_view(), name="usuarios"),
    path("usuarios/<uuid:usuario_id>", UsuarioDetailView.as_view(), name="usuario-detalle"),
]
