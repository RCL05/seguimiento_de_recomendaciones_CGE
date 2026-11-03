from django.test import TestCase

from backend.core.audit.models import AuditLog
from backend.modules.notificaciones.application.manage_notification_settings import (
    ManageNotificationSettingsUseCase,
)
from backend.modules.usuarios.application.login_sso import LoginSsoUseCase
from backend.modules.usuarios.application.manage_roles import ManageRolesUseCase
from backend.modules.usuarios.application.manage_units import ManageUnitsUseCase
from backend.modules.usuarios.models import Usuario
from uuid import uuid4


class IdentityConfigurationFlowTests(TestCase):
    def test_flujo_completo_de_identidad_y_configuracion(self):
        login = LoginSsoUseCase()
        dti_identity = login.execute(token="dti-sso-token", request_id=uuid4())
        self.assertEqual(dti_identity["rol"], "DTI")

        user_identity = login.execute(
            token="valid-sso-token",
            request_id=uuid4(),
            ip_address="127.0.0.1",
        )
        self.assertEqual(user_identity["rol"], "UAI")

        dti = Usuario.objects.get(correo_institucional="dti@unl.edu.ec")
        uai = Usuario.objects.get(correo_institucional="uai@unl.edu.ec")

        units = ManageUnitsUseCase()
        unit = units.create_or_update_unit(
            actor=dti,
            codigo="CONTABILIDAD",
            nombre="Unidad de Contabilidad",
            request_id=uuid4(),
        )
        units.reassign_user(
            actor=dti,
            target=uai,
            unidad=unit,
            request_id=uuid4(),
        )
        uai.refresh_from_db()
        self.assertEqual(uai.unidad_org_id, unit.id)

        roles = ManageRolesUseCase()
        roles.assign_role(
            actor=dti,
            target=uai,
            new_role=Usuario.Rol.RECTORADO,
            request_id=uuid4(),
        )
        uai.refresh_from_db()
        self.assertEqual(uai.rol, Usuario.Rol.RECTORADO)

        settings = ManageNotificationSettingsUseCase()
        config = settings.update_settings(
            actor=dti,
            values={"umbral_dias": 10, "destinatarios_vencimiento": ["UAI"]},
            request_id=uuid4(),
        )
        self.assertEqual(config.umbral_dias, 10)

        actions = set(
            AuditLog.objects.filter(usuario=dti).values_list("accion", flat=True)
        )
        self.assertIn("LOGIN_SSO", actions)
        self.assertIn("MANAGE_UNIT", actions)
        self.assertIn("REASSIGN_USER", actions)
        self.assertIn("ASSIGN_ROLE", actions)
        self.assertIn("UPDATE_NOTIFICATION_SETTINGS", actions)

        reassignment = AuditLog.objects.get(accion="REASSIGN_USER")
        self.assertEqual(reassignment.estado_anterior, None)
        self.assertIn("new_unit", reassignment.detalles_json)
