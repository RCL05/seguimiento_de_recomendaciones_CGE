from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Asignacion, EstadoEvidencia, Evidencia, Recomendacion, Responsable, Unidad
from .serializers import (
    AnularEvidenciaSerializer,
    AsignacionSerializer,
    EvidenciaSerializer,
    RecomendacionSerializer,
    ResponsableSerializer,
    UnidadSerializer,
)


class UnidadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["nombre", "siglas"]


class ResponsableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Responsable.objects.select_related("unidad").all()
    serializer_class = ResponsableSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["nombre", "cargo", "email"]
    filterset_fields = ["unidad", "activo"]


class RecomendacionViewSet(viewsets.ModelViewSet):
    serializer_class = RecomendacionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["codigo", "descripcion"]
    filterset_fields = ["estado", "prioridad"]
    ordering_fields = ["fecha_limite", "fecha_emision", "creado_en"]

    def get_queryset(self):
        return (
            Recomendacion.objects.prefetch_related("asignaciones__responsable__unidad", "evidencias")
            .all()
        )

    def _sincronizar_responsables(self, recomendacion, responsables):
        if responsables is None:
            return
        recomendacion.asignaciones.all().delete()
        for responsable in responsables:
            Asignacion.objects.create(recomendacion=recomendacion, responsable=responsable)

    def perform_create(self, serializer):
        with transaction.atomic():
            recomendacion = serializer.save()
            self._sincronizar_responsables(
                recomendacion, serializer.validated_data.get("responsables")
            )

    def perform_update(self, serializer):
        with transaction.atomic():
            recomendacion = serializer.save()
            self._sincronizar_responsables(
                recomendacion, serializer.validated_data.get("responsables")
            )

    @action(detail=True, methods=["post"], url_path="evidencias")
    def cargar_evidencia(self, request, pk=None):
        recomendacion = self.get_object()
        serializer = EvidenciaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(recomendacion=recomendacion, cargado_por=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EvidenciaViewSet(viewsets.ModelViewSet):
    serializer_class = EvidenciaSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["recomendacion__codigo", "descripcion", "hash_archivo"]
    filterset_fields = ["estado", "tipo", "recomendacion"]

    def get_queryset(self):
        return Evidencia.objects.select_related("recomendacion", "cargado_por").all()

    def perform_create(self, serializer):
        serializer.save(cargado_por=self.request.user)

    @action(detail=True, methods=["patch"], url_path="anulacion")
    def anulacion(self, request, pk=None):
        evidencia = self.get_object()
        if evidencia.estado == EstadoEvidencia.ANULADA:
            return Response(
                {"detalle": "La evidencia ya está anulada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entrada = AnularEvidenciaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        evidencia.anular(
            motivo=entrada.validated_data.get("motivo")
            or "Anulación solicitada vía API."
        )
        return Response(EvidenciaSerializer(evidencia, context={"request": request}).data)
