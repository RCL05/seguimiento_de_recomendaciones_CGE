import hashlib
import json
import shutil
import tempfile
import uuid

from django.test import Client, TestCase, override_settings

from backend.core.audit.models import AuditLog
from backend.modules.usuarios.models import UnidadOrganica

PDF_BYTES = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


class QuickstartSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.media_root = tempfile.mkdtemp(prefix="sitra-quickstart-")
        self.addCleanup(shutil.rmtree, self.media_root, True)
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)

        for codigo in ("DEP-A", "DEP-B"):
            UnidadOrganica.objects.create(
                id=uuid.uuid5(uuid.NAMESPACE_URL, f"sitra-unit:{codigo}"),
                codigo=codigo,
                nombre=f"Dependencia {codigo}",
            )

    def _post(self, path, payload, role, user, unit):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_ROLE=role,
            HTTP_X_USER_ID=user,
            HTTP_X_UNIT_ID=unit,
        )

    def _create_recommendation(self, number="REC-QS-001"):
        report = self._post(
            "/api/v1/informes",
            {
                "numero_informe": f"INF-QS-{number}",
                "periodo_auditado": "2026",
                "fecha_notificacion": "2026-01-15",
                "pdf_informe_url": "https://example.test/informe.pdf",
            },
            "UAI",
            "uai-quickstart",
            "UAI",
        )
        self.assertEqual(report.status_code, 201, report.content)
        recommendation = self._post(
            "/api/v1/recomendaciones",
            {
                "report_id": report.json()["data"]["id"],
                "number": number,
                "description": "Implementar controles internos.",
                "unit_id": "DEP-A",
                "legal_days": 30,
                "due_date": "2026-02-14",
                "priority": "ALTA",
            },
            "UAI",
            "uai-quickstart",
            "UAI",
        )
        self.assertEqual(recommendation.status_code, 201, recommendation.content)
        return recommendation.json()["data"]["id"]

    def _start_execution(self, recommendation_id):
        plan = self._post(
            f"/api/v1/recomendaciones/{recommendation_id}/plan-accion",
            {"descripcion_hito": "Documentar controles", "fecha_compromiso": "2026-01-30"},
            "EJECUTOR",
            "ejecutor-a",
            "DEP-A",
        )
        self.assertEqual(plan.status_code, 201, plan.content)
        return plan

    def _upload(self, recommendation_id, content=PDF_BYTES):
        return self.client.post(
            f"/api/v1/recomendaciones/{recommendation_id}/evidencias",
            data=content,
            content_type="application/pdf",
            HTTP_X_FILENAME="evidencia.pdf",
            HTTP_X_ROLE="EJECUTOR",
            HTTP_X_USER_ID="ejecutor-a",
            HTTP_X_UNIT_ID="DEP-A",
        )

    def test_flujo_principal_aprobacion_y_cadena_de_auditoria(self):
        recommendation_id = self._create_recommendation()
        self._start_execution(recommendation_id)

        upload = self._upload(recommendation_id)
        self.assertEqual(upload.status_code, 201, upload.content)
        evidence = upload.json()["data"]
        self.assertEqual(evidence["sha256"], hashlib.sha256(PDF_BYTES).hexdigest())

        detail = self.client.get(
            f"/api/v1/recomendaciones/{recommendation_id}",
            HTTP_X_ROLE="UAI",
            HTTP_X_USER_ID="uai-quickstart",
        )
        self.assertEqual(detail.json()["data"]["state"], "EN_REVISION_INTERNA")
        self.assertEqual(len(detail.json()["data"]["evidencias"]), 1)

        dictamen = self.client.patch(
            f"/api/v1/recomendaciones/{recommendation_id}/dictamen",
            data=json.dumps(
                {
                    "evidence_id": evidence["id"],
                    "approved": True,
                    "observaciones": "Evidencia suficiente.",
                }
            ),
            content_type="application/json",
            HTTP_X_ROLE="UAI",
            HTTP_X_USER_ID="uai-quickstart",
        )
        self.assertEqual(dictamen.status_code, 200, dictamen.content)
        self.assertEqual(dictamen.json()["data"]["state"], "CUMPLIDA")

        actions = list(
            AuditLog.objects.filter(entidad_id=recommendation_id).values_list(
                "accion", flat=True
            )
        )
        for expected in ("CREATE", "CREATE_PLAN", "UPLOAD_EVIDENCE", "ISSUE_DICTAMEN"):
            self.assertIn(expected, actions)

    def test_rechazo_conserva_evidencia_y_permite_corregir(self):
        recommendation_id = self._create_recommendation("REC-QS-002")
        self._start_execution(recommendation_id)
        first = self._upload(recommendation_id).json()["data"]

        rejection = self.client.patch(
            f"/api/v1/recomendaciones/{recommendation_id}/dictamen",
            data=json.dumps(
                {
                    "evidence_id": first["id"],
                    "approved": False,
                    "observaciones": "Falta firma del responsable.",
                }
            ),
            content_type="application/json",
            HTTP_X_ROLE="UAI",
            HTTP_X_USER_ID="uai-quickstart",
        )
        self.assertEqual(rejection.status_code, 200, rejection.content)
        self.assertEqual(rejection.json()["data"]["state"], "RECHAZADA_CORRECCION")

        detail = self.client.get(
            f"/api/v1/recomendaciones/{recommendation_id}",
            HTTP_X_ROLE="UAI",
            HTTP_X_USER_ID="uai-quickstart",
        )
        self.assertEqual(len(detail.json()["data"]["evidencias"]), 1)

        corrected = self._upload(recommendation_id, PDF_BYTES + b"% correccion\n")
        self.assertEqual(corrected.status_code, 201, corrected.content)
        self.assertEqual(corrected.json()["data"]["recommendation_id"], recommendation_id)

    def test_bola_entre_unidades_responde_404_y_audita_el_intento(self):
        recommendation_id = self._create_recommendation("REC-QS-003")

        response = self.client.get(
            f"/api/v1/recomendaciones/{recommendation_id}",
            HTTP_X_ROLE="EJECUTOR",
            HTTP_X_USER_ID="ejecutor-b",
            HTTP_X_UNIT_ID="DEP-B",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertTrue(
            AuditLog.objects.filter(
                entidad_id=recommendation_id,
                accion="ACCESS_DENIED",
                resultado="DENIED",
            ).exists()
        )

    def test_matriz_csv_restingida_por_rol(self):
        forbidden = self.client.post(
            "/api/v1/reportes/matriz-cge",
            HTTP_X_ROLE="EJECUTOR",
            HTTP_X_USER_ID="ejecutor-a",
            HTTP_X_UNIT_ID="DEP-A",
        )
        self.assertEqual(forbidden.status_code, 403)

        allowed = self.client.post(
            "/api/v1/reportes/matriz-cge",
            HTTP_X_ROLE="CGE_AUDITOR",
            HTTP_X_USER_ID="auditor-quickstart",
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed["Content-Type"], "text/csv; charset=utf-8")
        self.assertTrue(allowed.content.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b"numero", allowed.content)
