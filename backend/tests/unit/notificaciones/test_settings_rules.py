from django.test import TestCase

from backend.core.shared.domain_types import PermissionDenied, ValidationError
from backend.modules.notificaciones.application.manage_notification_settings import (
    ManageNotificationSettingsUseCase,
    resolve_channels,
)
from backend.modules.notificaciones.infrastructure.preferences_models import (
    ConfiguracionNotificacion,
    PreferenciaNotificacion,
    TipoAlerta,
)
from backend.modules.usuarios.models import Usuario


class NotificationSettingsRulesTests(TestCase):
    def setUp(self):
        self.dti = Usuario.objects.create(
            correo_institucional="dti@unl.edu.ec",
            nombres="DTI",
            rol=Usuario.Rol.DTI,
        )
        self.uai = Usuario.objects.create(
            correo_institucional="uai@unl.edu.ec",
            nombres="UAI",
            rol=Usuario.Rol.UAI,
        )
        self.ejecutor = Usuario.objects.create(
            correo_institucional="ejecutor@unl.edu.ec",
            nombres="Ejecutor",
            rol=Usuario.Rol.EJECUTOR,
        )
        self.use_case = ManageNotificationSettingsUseCase()

    def test_dti_actualiza_umbral_destinatarios_y_canales_sin_secretos(self):
        config = self.use_case.update_settings(
            actor=self.dti,
            values={
                "umbral_dias": 20,
                "canal_email_activo": False,
                "destinatarios_mora": ["UAI", "RECTORADO"],
            },
        )
        config.refresh_from_db()
        self.assertEqual(config.umbral_dias, 20)
        self.assertFalse(config.canal_email_activo)
        self.assertEqual(config.destinatarios_mora, ["UAI", "RECTORADO"])
        self.assertNotIn("smtp_password", {field.name for field in config._meta.fields})

        with self.assertRaises(ValidationError):
            self.use_case.update_settings(
                actor=self.dti,
                values={"smtp_password": "no-debe-guardarse"},
            )

        with self.assertRaises(ValidationError):
            self.use_case.update_settings(actor=self.dti, values={"campo_desconocido": 1})

    def test_umbral_y_destinatarios_invalidos(self):
        with self.assertRaises(ValidationError):
            self.use_case.update_settings(actor=self.dti, values={"umbral_dias": 0})
        with self.assertRaises(ValidationError):
            self.use_case.update_settings(actor=self.dti, values={"umbral_dias": 91})
        with self.assertRaises(ValidationError):
            self.use_case.update_settings(actor=self.dti, values={"umbral_dias": "15"})
        with self.assertRaises(ValidationError):
            self.use_case.update_settings(
                actor=self.dti,
                values={"destinatarios_mora": ["INVITADO"]},
            )

    def test_solo_dti_configura_y_segregacion_de_funciones(self):
        with self.assertRaises(PermissionDenied):
            self.use_case.update_settings(actor=self.uai, values={"umbral_dias": 10})
        with self.assertRaises(PermissionDenied):
            self.use_case.update_settings(actor=self.ejecutor, values={"umbral_dias": 10})
        with self.assertRaises(PermissionDenied):
            self.use_case.get_settings(actor=self.uai)

    def test_preferencias_unicas_por_usuario_y_tipo(self):
        self.use_case.update_preferences(
            actor=self.ejecutor,
            target=self.ejecutor,
            preferences=[
                {
                    "tipo_alerta": TipoAlerta.ALERTA_VENCIMIENTO,
                    "notificar_email": False,
                }
            ],
        )
        self.use_case.update_preferences(
            actor=self.ejecutor,
            target=self.ejecutor,
            preferences=[
                {
                    "tipo_alerta": TipoAlerta.ALERTA_VENCIMIENTO,
                    "notificar_email": True,
                    "activo": False,
                }
            ],
        )
        preferences = PreferenciaNotificacion.objects.filter(usuario=self.ejecutor)
        self.assertEqual(preferences.count(), 1)
        self.assertTrue(preferences.first().notificar_email)
        self.assertFalse(preferences.first().activo)

    def test_usuario_no_puede_modificar_preferencias_de_otro(self):
        with self.assertRaises(PermissionDenied):
            self.use_case.update_preferences(
                actor=self.ejecutor,
                target=self.uai,
                preferences=[{"tipo_alerta": TipoAlerta.EN_MORA}],
            )

    def test_canales_efectivos_respetan_configuracion_y_preferencia(self):
        config = ConfiguracionNotificacion.load()
        config.canal_email_activo = False
        config.save()

        internal, email = resolve_channels(
            recipient=self.ejecutor,
            notification_type=TipoAlerta.ALERTA_VENCIMIENTO,
            config=config,
        )
        self.assertTrue(internal)
        self.assertFalse(email)

        self.use_case.update_preferences(
            actor=self.ejecutor,
            target=self.ejecutor,
            preferences=[
                {
                    "tipo_alerta": TipoAlerta.ALERTA_VENCIMIENTO,
                    "notificar_interno": False,
                    "notificar_email": True,
                }
            ],
        )
        internal, email = resolve_channels(
            recipient=self.ejecutor,
            notification_type=TipoAlerta.ALERTA_VENCIMIENTO,
            config=config,
        )
        self.assertFalse(internal)
        self.assertFalse(email)
