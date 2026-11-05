"""Caso de uso: registrar un informe de examen especial de la CGE (RF-005)."""
from datetime import date
from uuid import UUID, uuid4

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import ConflictError
from backend.modules.recomendaciones.infrastructure.repositories import ReportRepository
from backend.modules.recomendaciones.models import InformeCGE
from backend.modules.usuarios.models import Usuario


class RegisterInforme:
    def __init__(self, repository: ReportRepository | None = None) -> None:
        self.repository = repository or ReportRepository()

    def execute(
        self,
        *,
        number: str,
        audited_period: str,
        notification_date: date,
        document_url: str = "",
        document_file: UploadedFile | None = None,
        creator: Usuario,
        request_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> InformeCGE:
        if self.repository.get_by_number(number):
            raise ConflictError("Ya existe un informe con ese número.")
        report = InformeCGE(
            numero_informe=number,
            periodo_auditado=audited_period,
            fecha_notificacion=notification_date,
            pdf_informe_url=document_url,
            pdf_informe=document_file,
            creado_por=creator,
        )
        try:
            with transaction.atomic():
                self.repository.save(report)
                record_audit(
                    request_id=request_id or uuid4(),
                    user=creator,
                    action="CREATE",
                    entity="informe_cge",
                    entity_id=report.id,
                    details={"numero_informe": number},
                    ip_address=ip_address,
                    modulo="informes_cge",
                )
            return report
        except Exception:
            if report.pdf_informe and report.pdf_informe.name:
                report.pdf_informe.storage.delete(report.pdf_informe.name)
            raise
