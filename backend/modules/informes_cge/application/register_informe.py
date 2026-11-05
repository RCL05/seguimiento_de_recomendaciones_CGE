from datetime import date
from django.core.files.uploadedfile import UploadedFile

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
    ) -> InformeCGE:
        if self.repository.get_by_number(number):
            raise ValueError("El número de informe ya existe.")
        report = InformeCGE(
            numero_informe=number,
            periodo_auditado=audited_period,
            fecha_notificacion=notification_date,
            pdf_informe_url=document_url,
            pdf_informe=document_file,
            creado_por=creator,
        )
        try:
            return self.repository.save(report)
        except Exception:
            if report.pdf_informe and report.pdf_informe.name:
                report.pdf_informe.storage.delete(report.pdf_informe.name)
            raise
