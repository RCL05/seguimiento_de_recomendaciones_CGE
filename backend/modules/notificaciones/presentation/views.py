"""Capa API del módulo de notificaciones: bandeja, preferencias, configuración y job de plazos."""
from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, extend_schema

from backend.core.api.base import ApiView, ok
from backend.core.api.schema import envelope, errors
from backend.core.auth.permissions import IsAuthenticatedActor, require_roles
from backend.core.shared.domain_types import NotFoundError, PermissionDenied, Role
from backend.modules.notificaciones.application.manage_notification_settings import (
    ManageNotificationSettingsUseCase,
)
from backend.modules.notificaciones.application.mark_overdue import mark_overdue_recommendations
from backend.modules.notificaciones.application.send_deadline_alerts import send_deadline_alerts
from backend.modules.notificaciones.infrastructure.preferences_models import (
    PreferenciaNotificacion,
    TipoAlerta,
)
from backend.modules.notificaciones.models import Notificacion
from backend.modules.notificaciones.presentation.serializers import (
    ConfiguracionSerializer,
    ConfiguracionUpdateSerializer,
    EjecucionPlazosSerializer,
    NotificacionSerializer,
    PreferenciasSerializer,
    PreferenciasUpdateSerializer,
)
from backend.modules.usuarios.models import Usuario


def _target_user(actor: Usuario, requested_id) -> Usuario:
    if not requested_id:
        return actor
    if str(requested_id) != str(actor.id) and actor.rol != Usuario.Rol.DTI:
        raise PermissionDenied("Solo el propio usuario o DTI puede consultar estas preferencias.")
    target = Usuario.objects.filter(pk=requested_id).first()
    if target is None:
        raise NotFoundError("Usuario no encontrado.")
    return target


def _preference_data(preference: PreferenciaNotificacion) -> dict:
    return {
        "id": preference.id,
        "usuario_id": preference.usuario_id,
        "tipo_alerta": preference.tipo_alerta,
        "notificar_interno": preference.notificar_interno,
        "notificar_email": preference.notificar_email,
        "activo": preference.activo,
        "actualizado_en": preference.actualizado_en,
    }


def _effective_preferences(target: Usuario) -> list[dict]:
    """Preferencias guardadas o, si no existen, los valores por defecto de cada tipo de alerta."""
    existing = {p.tipo_alerta: p for p in PreferenciaNotificacion.objects.filter(usuario=target)}
    defaults = {
        "id": None,
        "usuario_id": target.id,
        "notificar_interno": True,
        "notificar_email": True,
        "activo": True,
        "actualizado_en": None,
    }
    return [
        _preference_data(existing[tipo]) if tipo in existing else {**defaults, "tipo_alerta": tipo}
        for tipo in TipoAlerta.values
    ]


class BandejaView(ApiView):
    @extend_schema(
        tags=["Notificaciones"],
        operation_id="consultarBandeja",
        summary="Consultar la bandeja de notificaciones del usuario autenticado",
        responses={200: envelope("Bandeja", NotificacionSerializer, many=True), **errors(401)},
    )
    def get(self, request):
        items = Notificacion.objects.filter(destinatario=self.actor).order_by("-programada_en")[:100]
        return ok(request, NotificacionSerializer(items, many=True).data, "Bandeja de notificaciones consultada")


class PreferenciasView(ApiView):
    @extend_schema(
        tags=["Notificaciones"],
        operation_id="consultarPreferencias",
        summary="Consultar preferencias de notificación",
        parameters=[OpenApiParameter("usuario_id", str, description="Solo DTI puede consultar a otro usuario.")],
        responses={200: envelope("Preferencias", PreferenciasSerializer), **errors(401, 403, 404)},
    )
    def get(self, request):
        target = _target_user(self.actor, request.query_params.get("usuario_id"))
        data = {"usuario_id": target.id, "preferencias": _effective_preferences(target)}
        return ok(request, PreferenciasSerializer(data).data, "Preferencias de notificación consultadas")

    @extend_schema(
        tags=["Notificaciones"],
        operation_id="actualizarPreferencias",
        summary="Reemplazar preferencias de notificación",
        request=PreferenciasUpdateSerializer,
        responses={200: envelope("PreferenciasActualizadas", PreferenciasSerializer), **errors(400, 401, 403, 404)},
    )
    def put(self, request):
        payload = PreferenciasUpdateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        target = _target_user(self.actor, payload.validated_data.get("usuario_id"))
        saved = ManageNotificationSettingsUseCase().update_preferences(
            actor=self.actor,
            target=target,
            preferences=payload.validated_data["preferencias"],
            request_id=self.request_id,
        )
        data = {"usuario_id": target.id, "preferencias": [_preference_data(item) for item in saved]}
        return ok(request, PreferenciasSerializer(data).data, "Preferencias de notificación actualizadas")


class ConfiguracionView(ApiView):
    @extend_schema(
        tags=["Notificaciones"],
        operation_id="consultarConfiguracionNotificaciones",
        summary="Consultar la configuración global de notificaciones",
        responses={200: envelope("Configuracion", ConfiguracionSerializer), **errors(401, 403)},
    )
    def get(self, request):
        config = ManageNotificationSettingsUseCase().get_settings(actor=self.actor)
        return ok(request, ConfiguracionSerializer(config).data, "Configuración de notificaciones consultada")

    @extend_schema(
        tags=["Notificaciones"],
        operation_id="actualizarConfiguracionNotificaciones",
        summary="Actualizar la configuración global de notificaciones (DTI)",
        request=ConfiguracionUpdateSerializer,
        responses={200: envelope("ConfiguracionActualizada", ConfiguracionSerializer), **errors(400, 401, 403)},
    )
    def put(self, request):
        config = ManageNotificationSettingsUseCase().update_settings(
            actor=self.actor,
            values=request.data,
            request_id=self.request_id,
        )
        return ok(request, ConfiguracionSerializer(config).data, "Configuración de notificaciones actualizada")


class EvaluacionPlazosView(ApiView):
    permission_classes = [
        IsAuthenticatedActor,
        require_roles(Role.DTI, message="Solo el rol DTI puede ejecutar los jobs."),
    ]

    @extend_schema(
        tags=["Notificaciones"],
        operation_id="evaluarPlazos",
        summary="Ejecutar la evaluación de plazos: alertas y vencimientos (DTI, RF-011, RF-012)",
        description="Normalmente lo invoca una tarea programada; es idempotente (RF-021).",
        request=None,
        responses={200: envelope("EjecucionPlazos", EjecucionPlazosSerializer), **errors(401, 403)},
    )
    def post(self, request):
        data = {
            "alertas_vencimiento": send_deadline_alerts(),
            "mora": mark_overdue_recommendations(),
        }
        return ok(request, data, "Jobs ejecutados correctamente")
