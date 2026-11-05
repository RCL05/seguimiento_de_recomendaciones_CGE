from uuid import UUID

from django.db import transaction
from django.db.models import Prefetch

from backend.modules.recomendaciones.models import Evidencia, InformeCGE, Recomendacion


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
        return self._with_list_relations().filter(
            unidad_responsable_id=unit_id
        ).order_by("-creada_en")

    def list_for_unit_code(self, unit_code: str):
        return self._with_list_relations().filter(
            unidad_responsable__codigo=unit_code
        ).order_by("-creada_en")

    def list_all(self):
        return self._with_list_relations().order_by("-creada_en")

    @staticmethod
    def filter_list(
        queryset,
        *,
        state: str | None = None,
        unit_code: str | None = None,
        priority: str | None = None,
        due_date=None,
        due_before=None,
        due_after=None,
    ):
        if state:
            queryset = queryset.filter(estado=state)
        if unit_code:
            queryset = queryset.filter(unidad_responsable__codigo=unit_code)
        if priority:
            queryset = queryset.filter(prioridad__iexact=priority)
        if due_date:
            queryset = queryset.filter(fecha_vencimiento_legal=due_date)
        if due_before:
            queryset = queryset.filter(fecha_vencimiento_legal__lte=due_before)
        if due_after:
            queryset = queryset.filter(fecha_vencimiento_legal__gte=due_after)
        return queryset

    def get_detail(self, recommendation_id: UUID) -> Recomendacion | None:
        evidences = Evidencia.objects.order_by("-fecha_carga")
        return (
            Recomendacion.objects.select_related("informe", "unidad_responsable")
            .prefetch_related(Prefetch("evidencias", queryset=evidences))
            .filter(pk=recommendation_id)
            .first()
        )

    @staticmethod
    def _with_list_relations():
        return Recomendacion.objects.select_related("informe", "unidad_responsable")

    @transaction.atomic
    def save(self, recommendation: Recomendacion) -> Recomendacion:
        recommendation.save()
        return recommendation
