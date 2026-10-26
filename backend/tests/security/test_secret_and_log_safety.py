import json
import logging

from django.test import Client, TestCase

from backend.core.audit.models import AuditLog
from backend.core.security.log_safety import REDACTED, redact_sensitive, safe_log_context
from backend.core.shared.domain_types import ValidationError
from backend.modules.notificaciones.application.manage_notification_settings import (
    ManageNotificationSettingsUseCase,
)
from backend.modules.notificaciones.infrastructure.preferences_models import (
    ConfiguracionNotificacion,
)
from backend.modules.usuarios.models import Usuario

SECRET_VALUE = "super-secreto-no-loggear"


class SecretAndLogSafetyTests(TestCase):
    def setUp(self):
        self.dti = Usuario.objects.create(
            correo_institucional="dti-seguridad@unl.edu.ec",
            nombres="DTI",
            rol=Usuario.Rol.DTI,
        )
        self.client = Client()

    def test_redaccion_recursiva_oculta_credenciales_y_conserva_ids(self):
        payload = {
            "request_id": "8d1f5c1e-0000-0000-0000-000000000001",
            "usuario": {"id": "u-1", "password": SECRET_VALUE},
            "headers": [
                {"Authorization": f"Bearer {SECRET_VALUE}"},
                {"X-Role": "DTI"},
            ],
            "smtp_password": SECRET_VALUE,
            "access_token": SECRET_VALUE,
            "client_secret": SECRET_VALUE,
            "hash_sha256": "a" * 64,
        }

        redacted = redact_sensitive(payload)

        self.assertEqual(redacted["request_id"], payload["request_id"])
        self.assertEqual(redacted["usuario"]["id"], "u-1")
        self.assertEqual(redacted["usuario"]["password"], REDACTED)
        self.assertEqual(redacted["headers"][0]["Authorization"], REDACTED)
        self.assertEqual(redacted["headers"][1]["X-Role"], "DTI")
        self.assertEqual(redacted["smtp_password"], REDACTED)
        self.assertEqual(redacted["access_token"], REDACTED)
        self.assertEqual(redacted["client_secret"], REDACTED)
        self.assertEqual(redacted["hash_sha256"], "a" * 64)
        self.assertNotIn(SECRET_VALUE, json.dumps(redacted))

    def test_logs_redactados_no_incluyen_el_secreto(self):
        logger = logging.getLogger("sitra.security.test")
        with self.assertLogs(logger, level="INFO") as captured:
            logger.info(
                "configuracion_recibida %s",
                safe_log_context(
                    usuario_id=str(self.dti.id),
                    smtp_password=SECRET_VALUE,
                    authorization=f"Bearer {SECRET_VALUE}",
                ),
            )

        output = "\n".join(captured.output)
        self.assertNotIn(SECRET_VALUE, output)
        self.assertIn(str(self.dti.id), output)
        self.assertIn(REDACTED, output)

    def test_configuracion_rechaza_secretos_sin_persistirlos_ni_auditarlos(self):
        use_case = ManageNotificationSettingsUseCase()

        with self.assertRaises(ValidationError):
            use_case.update_settings(
                actor=self.dti,
                values={"umbral_dias": 10, "smtp_password": SECRET_VALUE},
            )

        config = ConfiguracionNotificacion.load()
        self.assertEqual(config.umbral_dias, 15)
        self.assertFalse(
            AuditLog.objects.filter(detalles_json__icontains=SECRET_VALUE).exists()
        )

    def test_api_no_ecoa_el_secreto_en_la_respuesta_de_error(self):
        response = self.client.put(
            "/api/v1/notificaciones/configuracion",
            data=json.dumps({"smtp_password": SECRET_VALUE}),
            content_type="application/json",
            HTTP_X_ROLE="DTI",
            HTTP_X_USER_ID="dti-api",
        )

        self.assertEqual(response.status_code, 400, response.content.decode("utf-8"))
        self.assertNotIn(SECRET_VALUE, response.content.decode("utf-8"))
        self.assertFalse(
            AuditLog.objects.filter(detalles_json__icontains=SECRET_VALUE).exists()
        )

    def test_auditoria_de_configuracion_valida_solo_guarda_campos_permitidos(self):
        self.client.put(
            "/api/v1/notificaciones/configuracion",
            data=json.dumps({"umbral_dias": 7, "canal_email_activo": False}),
            content_type="application/json",
            HTTP_X_ROLE="DTI",
            HTTP_X_USER_ID="dti-api",
        )

        audit = AuditLog.objects.filter(
            modulo="notificaciones",
            accion="UPDATE_NOTIFICATION_SETTINGS",
        ).latest("id")
        serialized = json.dumps(audit.detalles_json)
        self.assertIn("umbral_dias", serialized)
        self.assertNotIn("password", serialized.lower())
        self.assertNotIn("token", serialized.lower())
        self.assertNotIn("secret", serialized.lower())
