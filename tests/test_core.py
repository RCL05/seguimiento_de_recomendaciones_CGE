from datetime import date, datetime
from zipfile import ZipFile
from io import BytesIO
import unittest

from seguimiento_cge.models import EstadoRecomendacion, InformeCGE, Recomendacion, Rol, Usuario
from seguimiento_cge.notifications import NotificationEngine, SemaforoColor
from seguimiento_cge.rbac import PermissionDeniedError, StateMachine
from seguimiento_cge.reports import ReportExporter


class FakeEmailGateway:
    def __init__(self):
        self.sent = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append((to, subject, body))


class StateMachineTests(unittest.TestCase):
    def test_responsable_can_transition_to_execution(self):
        sm = StateMachine()
        actor = Usuario(1, "Resp", "resp@test.local", Rol.RESPONSABLE_EJECUTOR)
        rec = Recomendacion(
            10,
            1,
            "R-1",
            "desc",
            EstadoRecomendacion.EN_PLANIFICACION,
            date(2026, 12, 1),
        )

        audit = sm.transition(rec, EstadoRecomendacion.EN_EJECUCION, actor)

        self.assertEqual(rec.estado_actual, EstadoRecomendacion.EN_EJECUCION)
        self.assertEqual(audit.valor_anterior, EstadoRecomendacion.EN_PLANIFICACION.value)
        self.assertEqual(audit.valor_nuevo, EstadoRecomendacion.EN_EJECUCION.value)

    def test_consultor_cannot_transition(self):
        sm = StateMachine()
        actor = Usuario(2, "Cons", "cons@test.local", Rol.CONSULTOR_OBSERVADOR)
        rec = Recomendacion(
            11,
            1,
            "R-2",
            "desc",
            EstadoRecomendacion.EN_EJECUCION,
            date(2026, 12, 1),
        )

        with self.assertRaises(PermissionDeniedError):
            sm.transition(rec, EstadoRecomendacion.EN_REVISION_UAI, actor)


class NotificationEngineTests(unittest.TestCase):
    def test_semaforo_thresholds(self):
        hoy = date(2026, 10, 8)
        self.assertEqual(
            NotificationEngine.semaforo(hoy, date(2026, 11, 20)), SemaforoColor.VERDE
        )
        self.assertEqual(
            NotificationEngine.semaforo(hoy, date(2026, 11, 7)), SemaforoColor.AMARILLO
        )
        self.assertEqual(
            NotificationEngine.semaforo(hoy, date(2026, 10, 22)), SemaforoColor.ROJO
        )
        self.assertEqual(
            NotificationEngine.semaforo(hoy, date(2026, 10, 7)), SemaforoColor.NEGRO
        )

    def test_notifications_send_email_and_return_alerts(self):
        gateway = FakeEmailGateway()
        engine = NotificationEngine(gateway)
        rec = Recomendacion(
            20,
            1,
            "R-20",
            "desc",
            EstadoRecomendacion.EN_EJECUCION,
            date(2026, 10, 18),
        )
        destinatario = Usuario(3, "Autoridad", "autoridad@test.local", Rol.MAXIMA_AUTORIDAD)

        alertas = engine.notificar([rec], [destinatario], date(2026, 10, 8))

        self.assertEqual(len(alertas), 1)
        self.assertEqual(alertas[0].color, SemaforoColor.ROJO)
        self.assertEqual(len(gateway.sent), 1)
        self.assertIn("[CGE][ROJO]", gateway.sent[0][1])


class ReportExporterTests(unittest.TestCase):
    def test_export_pdf_has_pdf_signature(self):
        informe = InformeCGE(1, "INF-001", "Examen", date(2026, 1, 1), "2025", "DTI")
        rec = Recomendacion(
            30,
            1,
            "R-30",
            "desc",
            EstadoRecomendacion.EN_REVISION_UAI,
            date(2026, 12, 20),
        )

        pdf = ReportExporter.export_matrix_to_pdf(informe, [rec])

        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(b"Matriz Institucional de Seguimiento CGE", pdf)

    def test_export_excel_has_xlsx_structure(self):
        informe = InformeCGE(1, "INF-002", "Examen", date(2026, 1, 1), "2025", "UAI")
        rec = Recomendacion(
            31,
            1,
            "R-31",
            "desc",
            EstadoRecomendacion.CERRADA,
            date(2026, 11, 1),
        )

        xlsx = ReportExporter.export_matrix_to_excel(informe, [rec])

        self.assertTrue(xlsx.startswith(b"PK"))
        with ZipFile(BytesIO(xlsx)) as zf:
            names = set(zf.namelist())
            self.assertIn("xl/workbook.xml", names)
            sheet = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
            self.assertIn("INF-002", sheet)
            self.assertIn("R-31", sheet)


if __name__ == "__main__":
    unittest.main()
