"""Capa API del módulo de usuarios: sesión SSO, unidades orgánicas y administración DTI."""
from __future__ import annotations

from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

from backend.core.api.base import ApiView, ok
from backend.core.api.schema import envelope, errors
from backend.core.auth.permissions import IsAuthenticatedActor, require_roles
from backend.core.shared.domain_types import NotFoundError, Role
from backend.modules.usuarios.application.list_units import ListUnits
from backend.modules.usuarios.application.login_sso import IniciarSesionSso
from backend.modules.usuarios.application.manage_roles import ManageRolesUseCase
from backend.modules.usuarios.application.manage_units import ManageUnitsUseCase
from backend.modules.usuarios.models import Usuario
from backend.modules.usuarios.presentation.serializers import (
    LoginSsoRequestSerializer,
    SesionSerializer,
    UnidadCreateSerializer,
    UnidadSerializer,
    UsuarioSerializer,
    UsuarioUpdateSerializer,
)

SOLO_DTI = require_roles(Role.DTI, message="Solo el rol DTI puede administrar usuarios y unidades.")


class LoginSsoView(ApiView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Autenticación"],
        operation_id="iniciarSesionSso",
        summary="Validar credencial institucional y emitir JWT",
        auth=[],
        request=LoginSsoRequestSerializer,
        responses={200: envelope("Sesion", SesionSerializer), **errors(400, 401)},
    )
    def post(self, request):
        payload = LoginSsoRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        session = IniciarSesionSso().execute(
            credential=payload.validated_data["credential"],
            request_id=self.request_id,
            ip_address=self.client_ip,
        )
        return ok(request, session, "Identidad institucional validada")


class UnidadListCreateView(ApiView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedActor(), SOLO_DTI()]
        return super().get_permissions()

    @extend_schema(
        tags=["Usuarios y unidades"],
        operation_id="listarUnidades",
        summary="Consultar el catálogo de unidades orgánicas (UAI, DTI)",
        responses={200: envelope("Unidades", UnidadSerializer, many=True), **errors(401, 403)},
    )
    def get(self, request):
        units = ListUnits().execute(actor=self.actor)
        return ok(request, UnidadSerializer(units, many=True).data, "Catálogo de unidades consultado")

    @extend_schema(
        tags=["Usuarios y unidades"],
        operation_id="registrarUnidad",
        summary="Registrar o renombrar una unidad orgánica (DTI)",
        request=UnidadCreateSerializer,
        responses={201: envelope("Unidad", UnidadSerializer), **errors(400, 401, 403)},
    )
    def post(self, request):
        payload = UnidadCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        unit = ManageUnitsUseCase().create_or_update_unit(
            actor=self.actor,
            codigo=payload.validated_data["codigo"],
            nombre=payload.validated_data["nombre"],
            request_id=self.request_id,
        )
        return ok(request, UnidadSerializer(unit).data, "Unidad registrada", status=201)


class UsuarioListView(ApiView):
    permission_classes = [IsAuthenticatedActor, SOLO_DTI]

    @extend_schema(
        tags=["Usuarios y unidades"],
        operation_id="listarUsuarios",
        summary="Consultar cuentas institucionales (DTI)",
        responses={200: envelope("Usuarios", UsuarioSerializer, many=True), **errors(401, 403)},
    )
    def get(self, request):
        users = Usuario.objects.select_related("unidad_org").order_by("correo_institucional")
        return ok(request, UsuarioSerializer(users, many=True).data, "Usuarios consultados")


class UsuarioDetailView(ApiView):
    permission_classes = [IsAuthenticatedActor, SOLO_DTI]

    @extend_schema(
        tags=["Usuarios y unidades"],
        operation_id="actualizarUsuario",
        summary="Asignar rol o cambiar la unidad de una cuenta (DTI, RF-002)",
        request=UsuarioUpdateSerializer,
        responses={200: envelope("Usuario", UsuarioSerializer), **errors(400, 401, 403, 404)},
    )
    def patch(self, request, usuario_id: UUID):
        target = Usuario.objects.select_related("unidad_org").filter(pk=usuario_id).first()
        if target is None:
            raise NotFoundError("Usuario no encontrado.")
        payload = UsuarioUpdateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        if "rol" in payload.validated_data:
            ManageRolesUseCase().assign_role(
                actor=self.actor,
                target=target,
                new_role=payload.validated_data["rol"],
                request_id=self.request_id,
            )
        if "unidad_codigo" in payload.validated_data:
            ManageUnitsUseCase().reassign_user(
                actor=self.actor,
                target=target,
                unidad=payload.validated_data["unidad_codigo"],
                request_id=self.request_id,
            )
        target.refresh_from_db()
        return ok(request, UsuarioSerializer(target).data, "Usuario actualizado")
