import shutil
import tempfile
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import EstadoEvidencia, Evidencia, Recomendacion
from .validators import validar_archivo_pdf


class ValidacionArchivoPdfTests(TestCase):
    def _pdf(self, nombre="evidencia.pdf", contenido=b"%PDF-1.4 contenido de prueba"):
        return SimpleUploadedFile(nombre, contenido, content_type="application/pdf")

    def test_acepta_pdf_valido(self):
        validar_archivo_pdf(self._pdf())

    def test_rechaza_extension_no_pdf(self):
        archivo = SimpleUploadedFile("nota.txt", b"%PDF-1.4", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validar_archivo_pdf(archivo)

    def test_rechaza_mime_incorrecto(self):
        archivo = SimpleUploadedFile("doc.pdf", b"%PDF-1.4", content_type="image/png")
        with self.assertRaises(ValidationError):
            validar_archivo_pdf(archivo)

    def test_rechaza_archivo_sin_cabecera_pdf(self):
        archivo = SimpleUploadedFile("doc.pdf", b"NO-ES-PDF", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validar_archivo_pdf(archivo)

    def test_rechaza_archivo_demasiado_grande(self):
        grande = b"%PDF-" + b"0" * (10 * 1024 * 1024)
        archivo = SimpleUploadedFile("grande.pdf", grande, content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validar_archivo_pdf(archivo)


class EvidenciaModeloTests(TestCase):
    def setUp(self):
        self._media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._media, ignore_errors=True)
        self.override = override_settings(MEDIA_ROOT=self._media)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.recomendacion = Recomendacion.objects.create(
            codigo="CGE-2026-099",
            descripcion="Prueba de evidencias.",
            fecha_emision=date.today(),
            fecha_limite=date.today() + timedelta(days=15),
        )

    def _crear(self):
        return Evidencia.objects.create(
            recomendacion=self.recomendacion,
            archivo=SimpleUploadedFile(
                "evidencia.pdf", b"%PDF-1.4 evidencia", content_type="application/pdf"
            ),
        )

    def test_calcula_tamano_y_hash(self):
        evidencia = self._crear()
        self.assertGreater(evidencia.tamano, 0)
        self.assertEqual(len(evidencia.hash_archivo), 64)
        self.assertEqual(evidencia.estado, EstadoEvidencia.VIGENTE)

    def test_anulacion_logica_conserva_registro(self):
        evidencia = self._crear()
        evidencia.anular(motivo="Evidencia errónea.")
        evidencia.refresh_from_db()
        self.assertTrue(evidencia.esta_anulada)
        self.assertEqual(evidencia.motivo_anulacion, "Evidencia errónea.")
        self.assertIsNotNone(evidencia.anulada_en)

    def test_no_se_puede_anular_dos_veces(self):
        evidencia = self._crear()
        evidencia.anular(motivo="Primera")
        with self.assertRaises(ValidationError):
            evidencia.anular(motivo="Segunda")


class VistasRecomendacionTests(TestCase):
    def setUp(self):
        self._media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._media, ignore_errors=True)
        self.override = override_settings(MEDIA_ROOT=self._media)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.user = get_user_model().objects.create_user(
            username="tester", password="clave-segura-123"
        )
        self.recomendacion = Recomendacion.objects.create(
            codigo="CGE-2026-050",
            descripcion="Vista de prueba.",
            fecha_emision=date.today(),
            fecha_limite=date.today() + timedelta(days=10),
        )

    def test_lista_requiere_autenticacion(self):
        respuesta = self.client.get(reverse("recomendaciones:recomendacion_lista"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/login/", respuesta.url)

    def test_lista_muestra_recomendaciones(self):
        self.client.force_login(self.user)
        respuesta = self.client.get(reverse("recomendaciones:recomendacion_lista"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "CGE-2026-050")

    def test_lista_filtra_por_estado(self):
        self.client.force_login(self.user)
        respuesta = self.client.get(
            reverse("recomendaciones:recomendacion_lista"),
            {"estado": "CUMPLIDA"},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, "CGE-2026-050")

    def test_detalle_responde(self):
        self.client.force_login(self.user)
        respuesta = self.client.get(
            reverse("recomendaciones:recomendacion_detalle", args=[self.recomendacion.pk])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "CGE-2026-050")

    def test_crear_recomendacion(self):
        self.client.force_login(self.user)
        respuesta = self.client.post(
            reverse("recomendaciones:recomendacion_crear"),
            {
                "codigo": "CGE-2026-051",
                "descripcion": "Creada desde la vista.",
                "origen": "CGE",
                "prioridad": "ALTA",
                "estado": "PENDIENTE",
                "fecha_emision": date.today().isoformat(),
                "fecha_limite": (date.today() + timedelta(days=20)).isoformat(),
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Recomendacion.objects.filter(codigo="CGE-2026-051").exists())


class VistasEvidenciaTests(TestCase):
    def setUp(self):
        self._media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._media, ignore_errors=True)
        self.override = override_settings(MEDIA_ROOT=self._media)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.user = get_user_model().objects.create_user(
            username="tester", password="clave-segura-123"
        )
        self.recomendacion = Recomendacion.objects.create(
            codigo="CGE-2026-060",
            descripcion="Evidencia desde vista.",
            fecha_emision=date.today(),
            fecha_limite=date.today() + timedelta(days=10),
        )

    def test_cargar_evidencia_pdf(self):
        self.client.force_login(self.user)
        archivo = SimpleUploadedFile(
            "evidencia.pdf", b"%PDF-1.4 evidencia", content_type="application/pdf"
        )
        respuesta = self.client.post(
            reverse("recomendaciones:evidencia_cargar", args=[self.recomendacion.pk]),
            {"archivo": archivo, "tipo": "FINAL", "descripcion": "Cumplimiento."},
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.recomendacion.evidencias.count(), 1)

    def test_rechaza_archivo_invalido(self):
        self.client.force_login(self.user)
        archivo = SimpleUploadedFile("evidencia.pdf", b"NO-PDF", content_type="application/pdf")
        respuesta = self.client.post(
            reverse("recomendaciones:evidencia_cargar", args=[self.recomendacion.pk]),
            {"archivo": archivo, "tipo": "FINAL"},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.recomendacion.evidencias.count(), 0)

    def test_anular_evidencia_conserva_registro(self):
        self.client.force_login(self.user)
        evidencia = Evidencia.objects.create(
            recomendacion=self.recomendacion,
            archivo=SimpleUploadedFile("e.pdf", b"%PDF-1.4 x", content_type="application/pdf"),
        )
        respuesta = self.client.post(
            reverse("recomendaciones:evidencia_anular", args=[evidencia.pk]),
            {"motivo": "Duplicada."},
        )
        self.assertEqual(respuesta.status_code, 302)
        evidencia.refresh_from_db()
        self.assertTrue(evidencia.esta_anulada)
        self.assertTrue(Evidencia.objects.filter(pk=evidencia.pk).exists())
