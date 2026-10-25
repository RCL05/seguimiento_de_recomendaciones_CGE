from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.core.audit.repository import record_audit
from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter
from backend.modules.usuarios.models import UnidadOrganica, Usuario


class LoginSsoUseCase:
    def __init__(self):
        self.sso = SsoAdapter()

    def execute(self, *, token: str, request_id=None, ip_address: str | None = None):
        identity = self.sso.authenticate(token=token)
        if not identity:
            raise PermissionError("Autenticación SSO inválida.")

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
            unidad, _ = UnidadOrganica.objects.get_or_create(codigo=unidad_codigo, defaults={"nombre": unidad_codigo})
            user.unidad_org = unidad
            user.save(update_fields=["unidad_org"])

        expira_en = datetime.now(timezone.utc) + timedelta(hours=8)
        try:
            if request_id:
                record_audit(
                    request_id=request_id,
                    user=user,
                    action="LOGIN_SSO",
                    entity="usuario",
                    entity_id=user.id,
                    details={"expira_en": expira_en.isoformat()},
                    ip_address=ip_address,
                    modulo="usuarios",
                )
        except Exception:
            pass
        return {"usuario_id": str(user.id), "rol": user.rol, "expira_en": expira_en.isoformat()}
