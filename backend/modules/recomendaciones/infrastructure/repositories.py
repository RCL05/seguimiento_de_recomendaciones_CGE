from uuid import UUID

from django.db import transaction

from backend.modules.recomendaciones.models import InformeCGE, Recomendacion


class ReportRepository:
    def get(self, report_id: UUID) -> InformeCGE | None:
        return InformeCGE.objects.select_related("creado_por").filter(pk=report_id).first()

    def get_by_number(self, number: str) -> InformeCGE | None:
        return InformeCGE.objects.filter(numero_informe=number).first()

    @transaction.atomic
    def save(self, report: InformeCGE) -> InformeCGE:
        report.save()
        return report


class RecommendationRepository:
    def get(self, recommendation_id: UUID, *, for_update: bool = False) -> Recomendacion | None:
        queryset = Recomendacion.objects.select_related("informe", "unidad_responsable")
        if for_update:
            queryset = queryset.select_for_update()
        return queryset.filter(pk=recommendation_id).first()

    def list_for_unit(self, unit_id: UUID):
        return Recomendacion.objects.filter(unidad_responsable_id=unit_id).order_by("-creada_en")

    @transaction.atomic
    def save(self, recommendation: Recomendacion) -> Recomendacion:
        recommendation.save()
        return recommendation
