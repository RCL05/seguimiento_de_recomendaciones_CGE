from datetime import date

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
        document_url: str,
        creator: Usuario,
    ) -> InformeCGE:
        if self.repository.get_by_number(number):
            raise ValueError("El número de informe ya existe.")
        report = InformeCGE(
            numero_informe=number,
            periodo_auditado=audited_period,
            fecha_notificacion=notification_date,
            pdf_informe_url=document_url,
            creado_por=creator,
        )
        return self.repository.save(report)
