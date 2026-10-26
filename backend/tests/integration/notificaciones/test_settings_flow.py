import json

from django.test import Client, TestCase

from backend.core.audit.models import AuditLog
from backend.modules.notificaciones.application.service import schedule_notification
from backend.modules.notificaciones.infrastructure.preferences_models import (
    ConfiguracionNotificacion,
    PreferenciaNotificacion,
    TipoAlerta,
)
from backend.modules.notificaciones.models import Notificacion
from backend.modules.usuarios.models import Usuario


class NotificationSettingsFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dti_configura_alertas_y_las_tareas_usan_la_configuracion(self):
        response = self.client.put(
            "/api/v1/notificaciones/configuracion",
            data=json.dumps(
                {
                    "umbral_dias": 30,
                    "notificaciones_activas": True,
                    "canal_email_activo": False,
                    "destinatarios_mora": ["UAI", "RECTORADO"],
                }
            ),
            content_type="application/json",
            HTTP_X_ROLE="DTI",
            HTTP_X_USER_ID="dti-config",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        config = ConfiguracionNotificacion.load()
        self.assertEqual(config.umbral_dias, 30)
        self.assertFalse(config.canal_email_activo)
        self.assertEqual(config.destinatarios_mora, ["UAI", "RECTORADO"])

        get_response = self.client.get(
            "/api/v1/notificaciones/configuracion",
            HTTP_X_ROLE="DTI",
            HTTP_X_USER_ID="dti-config",
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["data"]["umbral_dias"], 30)

    def test_consulta_y_actualizacion_de_preferencias_del_propio_usuario(self):
        response = self.client.put(
            "/api/v1/notificaciones/preferencias",
            data=json.dumps(
                {
                    "preferencias": [
                        {
                            "tipo_alerta": TipoAlerta.EN_MORA,
                            "notificar_email": False,
                        }
                    ]
                }
            ),
            content_type="application/json",
            HTTP_X_ROLE="EJECUTOR",
            HTTP_X_USER_ID="ejecutor-prefs",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["data"]["preferencias"][0]["notificar_email"])

        actor = Usuario.objects.get(correo_institucional="ejecutor-prefs@unl.edu.ec")
        self.assertTrue(
            PreferenciaNotificacion.objects.filter(
                usuario=actor,
                tipo_alerta=TipoAlerta.EN_MORA,
                notificar_email=False,
            ).exists()
        )

        get_response = self.client.get(
            "/api/v1/notificaciones/preferencias",
            HTTP_X_ROLE="EJECUTOR",
            HTTP_X_USER_ID="ejecutor-prefs",
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.json()["data"]["preferencias"]), len(TipoAlerta.values))

    def test_usuario_no_puede_consultar_preferencias_de_otro(self):
        target = Usuario.objects.create(
            correo_institucional="otro@unl.edu.ec",
            nombres="Otro",
            rol=Usuario.Rol.UAI,
        )
        response = self.client.get(
            f"/api/v1/notificaciones/preferencias?usuario_id={target.id}",
            HTTP_X_ROLE="EJECUTOR",
            HTTP_X_USER_ID="ejecutor-prefs-2",
        )
        self.assertEqual(response.status_code, 403)

    def test_cambios_de_configuracion_y_preferencias_quedan_auditados(self):
        self.client.put(
            "/api/v1/notificaciones/configuracion",
            data=json.dumps({"umbral_dias": 12}),
            content_type="application/json",
            HTTP_X_ROLE="DTI",
            HTTP_X_USER_ID="dti-audit",
        )
        self.client.put(
            "/api/v1/notificaciones/preferencias",
            data=json.dumps(
                {
                    "preferencias": [
                        {"tipo_alerta": TipoAlerta.ALERTA_VENCIMIENTO, "activo": True}
                    ]
                }
            ),
            content_type="application/json",
            HTTP_X_ROLE="UAI",
            HTTP_X_USER_ID="uai-audit",
        )
        actions = set(
            AuditLog.objects.filter(modulo="notificaciones").values_list("accion", flat=True)
        )
        self.assertIn("UPDATE_NOTIFICATION_SETTINGS", actions)
        self.assertIn("UPDATE_NOTIFICATION_PREFERENCES", actions)

    def test_notificaciones_idempotentes_y_canales_configurados(self):
        recipient = Usuario.objects.create(
            correo_institucional="destino@unl.edu.ec",
            nombres="Destino",
            rol=Usuario.Rol.UAI,
        )
        first = schedule_notification(
            recommendation=None,
            recipient=recipient,
            notification_type=TipoAlerta.EN_MORA,
            idempotency_key="MORA:demo:1",
        )
        second = schedule_notification(
            recommendation=None,
            recipient=recipient,
            notification_type=TipoAlerta.EN_MORA,
            idempotency_key="MORA:demo:1",
        )
        self.assertIsNotNone(first)
        self.assertEqual(first.id, second.id)
        self.assertEqual(Notificacion.objects.count(), 1)

        config = ConfiguracionNotificacion.load()
        config.notificaciones_activas = False
        config.save()
        suppressed = schedule_notification(
            recommendation=None,
            recipient=recipient,
            notification_type=TipoAlerta.EN_MORA,
            idempotency_key="MORA:demo:2",
        )
        self.assertIsNone(suppressed)
        self.assertEqual(Notificacion.objects.count(), 1)
