from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import AuthenticationRequired
from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter
from backend.modules.usuarios.models import UnidadOrganica, Usuario


class LoginSsoUseCase:
    def __init__(self):
        self.sso = SsoAdapter()

    def execute(self, *, token: str, request_id=None, ip_address: str | None = None):
        identity = self.sso.authenticate(token=token)
        if not identity:
            raise PermissionError("Autenticación SSO inválida.")

        expira_en = datetime.now(timezone.utc) + timedelta(hours=8)
        with transaction.atomic():
            correo = identity.get("correo")
            user, _ = Usuario.objects.get_or_create(
                correo_institucional=correo,
                defaults={
                    "nombres": identity.get("nombres", ""),
                    "rol": identity.get("rol", Usuario.Rol.EJECUTOR),
                    "activo": True,
                },
            )
            unidad_codigo = identity.get("unidad_codigo")
            if unidad_codigo and not user.unidad_org:
                unidad, _ = UnidadOrganica.objects.get_or_create(
                    codigo=unidad_codigo,
                    defaults={"nombre": unidad_codigo},
                )
                user.unidad_org = unidad
                user.save(update_fields=["unidad_org"])

            record_audit(
                request_id=request_id or uuid4(),
                user=user,
                action="LOGIN_SSO",
                entity="usuario",
                entity_id=user.id,
                details={"expira_en": expira_en.isoformat()},
                ip_address=ip_address,
                modulo="usuarios",
            )
            return {"usuario_id": str(user.id), "rol": user.rol, "expira_en": expira_en.isoformat()}


class IniciarSesionSso:
    """Valida la credencial SSO, sincroniza la cuenta y emite el JWT de sesión (RF-001)."""

    def __init__(self, sso: SsoAdapter | None = None):
        self.sso = sso or SsoAdapter()

    def execute(self, *, credential: str, request_id=None, ip_address: str | None = None) -> dict:
        identity = self.sso.authenticate(token=credential)
        if not identity:
            raise AuthenticationRequired("La credencial SSO no es válida.")

        with transaction.atomic():
            actor, _ = Usuario.objects.get_or_create(
                correo_institucional=identity["correo"],
                defaults={
                    "nombres": identity.get("nombres") or identity["correo"],
                    "rol": identity["rol"],
                    "activo": True,
                },
            )
            if not actor.activo:
                raise AuthenticationRequired("La identidad no está habilitada en el sistema.")
            unidad_codigo = identity.get("unidad_codigo")
            if actor.unidad_org_id is None and unidad_codigo:
                unidad, _ = UnidadOrganica.objects.get_or_create(
                    codigo=unidad_codigo,
                    defaults={"nombre": unidad_codigo},
                )
                actor.unidad_org = unidad
                actor.save(update_fields=["unidad_org"])

            unit_code = actor.unidad_org.codigo if actor.unidad_org_id else None
            access_token = self.sso.issue_session(
                {
                    "user_id": str(actor.id),
                    "email": actor.correo_institucional,
                    "role": actor.rol,
                    "unit_id": unit_code,
                }
            )
            record_audit(
                request_id=request_id or uuid4(),
                user=actor,
                action="LOGIN_SSO",
                entity="usuario",
                entity_id=actor.id,
                details={"expires_in": SsoAdapter.token_ttl_seconds},
                ip_address=ip_address,
                modulo="usuarios",
            )
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": SsoAdapter.token_ttl_seconds,
            "user_id": str(actor.id),
            "email": actor.correo_institucional,
            "display_name": actor.nombres,
            "role": actor.rol,
            "unit_id": unit_code,
        }
