from datetime import date
from uuid import UUID

from django.db import transaction
from django.db.models import BooleanField, Case, Exists, OuterRef, Prefetch, Q, Value, When
from django.utils import timezone

from backend.modules.recomendaciones.models import Evidencia, InformeCGE, Recomendacion


def anotar_vencimiento(queryset, hoy: date | None = None):
    """Agrega `entrega_oportuna` y `vencida` calculados en SQL (regla de domain/vencimiento.py).

    `entrega_oportuna`: existe una evidencia vigente, cargada hasta la fecha de
    vencimiento (hora local) y todavía sin dictamen UAI.
    """
    hoy = hoy or timezone.localdate()
    entrega_oportuna = Evidencia.objects.filter(
        recomendacion=OuterRef("pk"),
        estado=Evidencia.Estado.VIGENTE,
        dictamenuai__isnull=True,
        fecha_carga__date__lte=OuterRef("fecha_vencimiento_legal"),
    )
    return queryset.annotate(entrega_oportuna=Exists(entrega_oportuna)).annotate(
        vencida=Case(
            When(
                Q(fecha_vencimiento_legal__lt=hoy)
                & ~Q(estado=Recomendacion.Estado.CUMPLIDA)
                & ~Q(estado=Recomendacion.Estado.EN_VALIDACION, entrega_oportuna=True),
                then=Value(True),
            ),
            default=Value(False),
            output_field=BooleanField(),
        )
    )


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
        overdue: bool | None = None,
    ):
        if overdue is not None:
            queryset = queryset.filter(vencida=overdue)
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
            anotar_vencimiento(Recomendacion.objects.select_related("informe", "unidad_responsable"))
            .prefetch_related(Prefetch("evidencias", queryset=evidences))
            .filter(pk=recommendation_id)
            .first()
        )

    @staticmethod
    def esta_vencida(recommendation_id: UUID) -> bool:
        return bool(
            anotar_vencimiento(Recomendacion.objects.filter(pk=recommendation_id))
            .values_list("vencida", flat=True)
            .first()
        )

    @staticmethod
    def _with_list_relations():
        return anotar_vencimiento(Recomendacion.objects.select_related("informe", "unidad_responsable"))

    @transaction.atomic
    def save(self, recommendation: Recomendacion) -> Recomendacion:
        recommendation.save()
        return recommendation
