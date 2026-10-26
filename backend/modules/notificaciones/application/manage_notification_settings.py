from __future__ import annotations

from backend.core.shared.domain_types import (
    PermissionDenied,
    Role,
    ValidationError,
)
from backend.modules.notificaciones.application.settings_audit_events import (
    audit_notification_settings_change,
)
from backend.modules.notificaciones.infrastructure.preferences_models import (
    ConfiguracionNotificacion,
    PreferenciaNotificacion,
    TipoAlerta,
)
from backend.modules.usuarios.models import Usuario

ALLOWED_SETTINGS = {
    "umbral_dias",
    "notificaciones_activas",
    "canal_interno_activo",
    "canal_email_activo",
    "destinatarios_vencimiento",
    "destinatarios_mora",
}

NOTIFICATION_ROLES = {
    Role.UAI.value,
    Role.EJECUTOR.value,
    Role.RECTORADO.value,
    Role.CGE_AUDITOR.value,
}

SECRET_HINTS = ("secret", "password", "passwd", "smtp", "token", "credential", "key")


class ManageNotificationSettingsUseCase:
    def get_settings(self, *, actor: Usuario) -> ConfiguracionNotificacion:
        if actor.rol != Usuario.Rol.DTI:
            raise PermissionDenied("Solo DTI puede consultar la configuración de notificaciones.")
        return ConfiguracionNotificacion.load()

    def update_settings(
        self,
        *,
        actor: Usuario,
        values: dict,
        request_id=None,
    ) -> ConfiguracionNotificacion:
        if actor.rol != Usuario.Rol.DTI:
            raise PermissionDenied("Solo DTI puede configurar las notificaciones.")

        if not isinstance(values, dict) or not values:
            raise ValidationError("Debe enviar al menos un valor de configuración.")

        suffix = _secret_key(values)
        if suffix:
            raise ValidationError(
                f"No se permite almacenar secretos en la configuración ({suffix})."
            )

        unknown = set(values) - ALLOWED_SETTINGS
        if unknown:
            raise ValidationError(
                "Campos de configuración no permitidos: " + ", ".join(sorted(unknown))
            )

        _validate_values(values)

        config = ConfiguracionNotificacion.load()
        previous = config.snapshot()
        for field, value in values.items():
            setattr(config, field, value)
        config.actualizado_por = actor
        config.save()

        audit_notification_settings_change(
            request_id=request_id,
            actor=actor,
            previous=previous,
            current=config.snapshot(),
        )
        return config

    def update_preferences(
        self,
        *,
        actor: Usuario,
        target: Usuario,
        preferences: list[dict],
        request_id=None,
    ) -> list[PreferenciaNotificacion]:
        if actor.id != target.id and actor.rol != Usuario.Rol.DTI:
            raise PermissionDenied(
                "Solo el propio usuario o DTI puede modificar sus preferencias."
            )
        if not isinstance(preferences, list) or not preferences:
            raise ValidationError("Debe enviar al menos una preferencia.")

        saved = []
        for item in preferences:
            if not isinstance(item, dict):
                raise ValidationError("Cada preferencia debe ser un objeto.")
            tipo = item.get("tipo_alerta")
            if tipo not in TipoAlerta.values:
                raise ValidationError(f"Tipo de alerta no válido: {tipo}.")
            for field in ("notificar_interno", "notificar_email", "activo"):
                if field in item and not isinstance(item[field], bool):
                    raise ValidationError(f"{field} debe ser booleano.")

            preference, _ = PreferenciaNotificacion.objects.update_or_create(
                usuario=target,
                tipo_alerta=tipo,
                defaults={
                    "notificar_interno": item.get("notificar_interno", True),
                    "notificar_email": item.get("notificar_email", True),
                    "activo": item.get("activo", True),
                },
            )
            saved.append(preference)

        audit_notification_settings_change(
            request_id=request_id,
            actor=actor,
            previous={},
            current={
                "usuario_id": str(target.id),
                "preferencias": [
                    {
                        "tipo_alerta": preference.tipo_alerta,
                        "notificar_interno": preference.notificar_interno,
                        "notificar_email": preference.notificar_email,
                        "activo": preference.activo,
                    }
                    for preference in saved
                ],
            },
            action="UPDATE_NOTIFICATION_PREFERENCES",
        )
        return saved


def _secret_key(values: dict) -> str | None:
    for key in values:
        lowered = str(key).lower()
        if any(hint in lowered for hint in SECRET_HINTS):
            return str(key)
    return None


def _validate_values(values: dict) -> None:
    if "umbral_dias" in values:
        threshold = values["umbral_dias"]
        if isinstance(threshold, bool) or not isinstance(threshold, int):
            raise ValidationError("El umbral de días debe ser un número entero.")
        if not 1 <= threshold <= 90:
            raise ValidationError("El umbral de días debe estar entre 1 y 90.")

    for field in (
        "notificaciones_activas",
        "canal_interno_activo",
        "canal_email_activo",
    ):
        if field in values and not isinstance(values[field], bool):
            raise ValidationError(f"{field} debe ser booleano.")

    for field in ("destinatarios_vencimiento", "destinatarios_mora"):
        if field not in values:
            continue
        recipients = values[field]
        if not isinstance(recipients, list) or not recipients:
            raise ValidationError(f"{field} debe ser una lista de roles no vacía.")
        invalid = [role for role in recipients if role not in NOTIFICATION_ROLES]
        if invalid:
            raise ValidationError(
                f"{field} contiene roles no válidos: " + ", ".join(map(str, invalid))
            )


def resolve_channels(
    *,
    recipient: Usuario,
    notification_type: str,
    config: ConfiguracionNotificacion | None = None,
) -> tuple[bool, bool]:
    """Resuelve los canales efectivos de una notificación.

    La configuración global actúa como techo; la preferencia del usuario solo
    puede desactivar canales, nunca activar uno deshabilitado globalmente.
    """
    config = config or ConfiguracionNotificacion.load()
    if not config.notificaciones_activas:
        return False, False

    preference = PreferenciaNotificacion.objects.filter(
        usuario=recipient,
        tipo_alerta=notification_type,
    ).first()
    if preference and not preference.activo:
        return False, False

    internal = config.canal_interno_activo
    email = config.canal_email_activo
    if preference:
        internal = internal and preference.notificar_interno
        email = email and preference.notificar_email
    return internal, email
