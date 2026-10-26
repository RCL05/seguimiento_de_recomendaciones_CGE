from __future__ import annotations

import json
import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.http import JsonResponse

from backend.core.api.error_catalog import error_response as domain_error_response
from backend.core.api.request_context import get_or_create_request_id
from backend.core.api.response_envelope import build_envelope, success_response
from backend.core.api.views import _persistent_user
from backend.core.shared.domain_types import (
    DomainError,
    NotFoundError,
    PermissionDenied,
)
from backend.modules.notificaciones.application.manage_notification_settings import (
    ManageNotificationSettingsUseCase,
)
from backend.modules.notificaciones.infrastructure.preferences_models import (
    ConfiguracionNotificacion,
    PreferenciaNotificacion,
    TipoAlerta,
)
from backend.modules.usuarios.models import Usuario


logger = logging.getLogger(__name__)


def _error_response(request, exc: Exception) -> JsonResponse:
    request_id = get_or_create_request_id(request)
    if isinstance(exc, DomainError):
        payload, status = domain_error_response(exc, request_id)
        return JsonResponse(payload, status=status)
    logger.exception("Error no controlado en configuración de notificaciones")
    payload = build_envelope(
        success=False,
        message="Ocurrió un error interno.",
        errors={"code": "INTERNAL_ERROR"},
        request_id=request_id,
    )
    return JsonResponse(payload, status=500)


def _payload(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError as error:
        raise DomainError("El cuerpo debe ser JSON vÃ¡lido.") from error


def _target_user(request, actor: Usuario, payload: dict | None = None) -> Usuario:
    payload = payload or {}
    requested_id = payload.get("usuario_id") or request.GET.get("usuario_id")
    if not requested_id:
        return actor
    if str(requested_id) != str(actor.id) and actor.rol != Usuario.Rol.DTI:
        raise PermissionDenied(
            "Solo el propio usuario o DTI puede consultar estas preferencias."
        )
    target = Usuario.objects.filter(pk=requested_id).first()
    if not target:
        raise NotFoundError("Usuario no encontrado.")
    return target


def _preference_data(preference: PreferenciaNotificacion) -> dict:
    return {
        "id": str(preference.id),
        "usuario_id": str(preference.usuario_id),
        "tipo_alerta": preference.tipo_alerta,
        "notificar_interno": preference.notificar_interno,
        "notificar_email": preference.notificar_email,
        "activo": preference.activo,
        "actualizado_en": preference.actualizado_en.isoformat(),
    }


def _settings_data(config: ConfiguracionNotificacion) -> dict:
    return {
        "umbral_dias": config.umbral_dias,
        "notificaciones_activas": config.notificaciones_activas,
        "canal_interno_activo": config.canal_interno_activo,
        "canal_email_activo": config.canal_email_activo,
        "destinatarios_vencimiento": list(config.destinatarios_vencimiento or []),
        "destinatarios_mora": list(config.destinatarios_mora or []),
        "actualizado_en": config.actualizado_en.isoformat(),
    }


def _effective_preferences(target: Usuario) -> list[dict]:
    existing = {
        preference.tipo_alerta: preference
        for preference in PreferenciaNotificacion.objects.filter(usuario=target)
    }
    items = []
    for tipo in TipoAlerta.values:
        preference = existing.get(tipo)
        if preference:
            items.append(_preference_data(preference))
        else:
            items.append(
                {
                    "id": None,
                    "usuario_id": str(target.id),
                    "tipo_alerta": tipo,
                    "notificar_interno": True,
                    "notificar_email": True,
                    "activo": True,
                    "actualizado_en": None,
                }
            )
    return items


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def notification_preferences(request):
    try:
        _, actor = _persistent_user(request)
        use_case = ManageNotificationSettingsUseCase()

        if request.method == "GET":
            target = _target_user(request, actor)
            return success_response(
                data={
                    "usuario_id": str(target.id),
                    "preferencias": _effective_preferences(target),
                },
                message="Preferencias de notificaciÃ³n consultadas",
            )

        payload = _payload(request)
        target = _target_user(request, actor, payload)
        saved = use_case.update_preferences(
            actor=actor,
            target=target,
            preferences=payload.get("preferencias"),
            request_id=get_or_create_request_id(request),
        )
        return success_response(
            data={
                "usuario_id": str(target.id),
                "preferencias": [_preference_data(item) for item in saved],
            },
            message="Preferencias de notificaciÃ³n actualizadas",
        )
    except Exception as exc:
        return _error_response(request, exc)


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def notification_settings(request):
    try:
        _, actor = _persistent_user(request)
        use_case = ManageNotificationSettingsUseCase()

        if request.method == "GET":
            config = use_case.get_settings(actor=actor)
            return success_response(
                data=_settings_data(config),
                message="ConfiguraciÃ³n de notificaciones consultada",
            )

        config = use_case.update_settings(
            actor=actor,
            values=_payload(request),
            request_id=get_or_create_request_id(request),
        )
        return success_response(
            data=_settings_data(config),
            message="ConfiguraciÃ³n de notificaciones actualizada",
        )
    except Exception as exc:
        return _error_response(request, exc)
