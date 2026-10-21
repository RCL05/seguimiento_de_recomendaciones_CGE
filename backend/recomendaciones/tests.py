from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

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
