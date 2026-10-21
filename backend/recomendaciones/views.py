from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EvidenciaForm, RecomendacionForm
from .models import (
    Asignacion,
    EstadoRecomendacion,
    Evidencia,
    Prioridad,
    Recomendacion,
)


@login_required
def recomendacion_lista(request):
    recomendaciones = Recomendacion.objects.prefetch_related("asignaciones__responsable")

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()
    prioridad = request.GET.get("prioridad", "").strip()

    if busqueda:
        recomendaciones = recomendaciones.filter(
            Q(codigo__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )
    if estado:
        recomendaciones = recomendaciones.filter(estado=estado)
    if prioridad:
        recomendaciones = recomendaciones.filter(prioridad=prioridad)

    contexto = {
        "recomendaciones": recomendaciones,
        "estados": EstadoRecomendacion.choices,
        "prioridades": Prioridad.choices,
        "filtro_q": busqueda,
        "filtro_estado": estado,
        "filtro_prioridad": prioridad,
        "total": recomendaciones.count(),
    }
    return render(request, "recomendaciones/recomendacion_lista.html", contexto)


@login_required
def recomendacion_detalle(request, pk):
    recomendacion = get_object_or_404(
        Recomendacion.objects.prefetch_related(
            "asignaciones__responsable__unidad", "evidencias"
        ),
        pk=pk,
    )
    return render(
        request,
        "recomendaciones/recomendacion_detalle.html",
        {
            "recomendacion": recomendacion,
            "form_evidencia": EvidenciaForm(),
        },
    )


@login_required
def recomendacion_crear(request):
    if request.method == "POST":
        form = RecomendacionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                recomendacion = form.save()
                for responsable in form.cleaned_data["responsables"]:
                    Asignacion.objects.create(
                        recomendacion=recomendacion, responsable=responsable
                    )
            messages.success(request, "Recomendación registrada correctamente.")
            return redirect("recomendaciones:recomendacion_detalle", pk=recomendacion.pk)
        messages.error(request, "Revise los errores del formulario.")
    else:
        form = RecomendacionForm()
    return render(
        request,
        "recomendaciones/recomendacion_form.html",
        {"form": form, "titulo": "Nueva recomendación"},
    )


@login_required
def recomendacion_editar(request, pk):
    recomendacion = get_object_or_404(Recomendacion, pk=pk)
    if request.method == "POST":
        form = RecomendacionForm(request.POST, instance=recomendacion)
        if form.is_valid():
            with transaction.atomic():
                recomendacion = form.save()
                recomendacion.asignaciones.all().delete()
                for responsable in form.cleaned_data["responsables"]:
                    Asignacion.objects.create(
                        recomendacion=recomendacion, responsable=responsable
                    )
            messages.success(request, "Recomendación actualizada correctamente.")
            return redirect("recomendaciones:recomendacion_detalle", pk=recomendacion.pk)
        messages.error(request, "Revise los errores del formulario.")
    else:
        form = RecomendacionForm(instance=recomendacion)
    return render(
        request,
        "recomendaciones/recomendacion_form.html",
        {"form": form, "titulo": f"Editar {recomendacion.codigo}", "recomendacion": recomendacion},
    )


@login_required
def evidencia_cargar(request, pk):
    recomendacion = get_object_or_404(Recomendacion, pk=pk)
    if request.method == "POST":
        form = EvidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            evidencia = form.save(commit=False)
            evidencia.recomendacion = recomendacion
            evidencia.cargado_por = request.user
            evidencia.save()
            messages.success(request, "Evidencia cargada y asociada a la recomendación.")
            return redirect("recomendaciones:recomendacion_detalle", pk=recomendacion.pk)
        messages.error(request, "No se pudo cargar la evidencia. Revise el archivo.")
        return render(
            request,
            "recomendaciones/recomendacion_detalle.html",
            {
                "recomendacion": recomendacion,
                "form_evidencia": form,
                "evidencias": recomendacion.evidencias.all(),
            },
        )
    return redirect("recomendaciones:recomendacion_detalle", pk=recomendacion.pk)


@login_required
def evidencia_anular(request, pk):
    evidencia = get_object_or_404(Evidencia, pk=pk)
    if request.method == "POST":
        if evidencia.esta_anulada:
            messages.warning(request, "La evidencia ya estaba anulada.")
        else:
            evidencia.anular(
                motivo=request.POST.get("motivo", "").strip()
                or "Anulación solicitada desde la interfaz."
            )
            messages.success(request, "Evidencia anulada. El registro se conserva.")
    return redirect(
        "recomendaciones:recomendacion_detalle", pk=evidencia.recomendacion_id
    )
