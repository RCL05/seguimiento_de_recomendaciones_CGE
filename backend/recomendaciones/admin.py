from django.contrib import admin, messages
from django.utils import timezone

from .models import (
    Asignacion,
    EstadoRecomendacion,
    Evidencia,
    Recomendacion,
    Responsable,
    Unidad,
)


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "siglas", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre", "siglas")


@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cargo", "unidad", "email", "activo")
    list_filter = ("activo", "unidad")
    search_fields = ("nombre", "cargo", "email")
    autocomplete_fields = ("unidad",)


class AsignacionInline(admin.TabularInline):
    model = Asignacion
    extra = 1
    autocomplete_fields = ("responsable",)


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    fields = ("archivo", "tipo", "estado", "descripcion", "creado_en")
    readonly_fields = ("creado_en",)
    show_change_link = True


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descripcion_corta",
        "prioridad",
        "estado",
        "fecha_limite",
        "esta_vencida",
        "creado_en",
    )
    list_filter = ("estado", "prioridad", "responsables__unidad")
    search_fields = ("codigo", "descripcion", "origen")
    date_hierarchy = "fecha_limite"
    readonly_fields = ("creado_en", "actualizado_en")
    inlines = (AsignacionInline, EvidenciaInline)
    filter_horizontal = ()
    actions = ("marcar_vencidas",)

    fieldsets = (
        ("Identificación", {"fields": ("codigo", "descripcion", "origen")}),
        ("Clasificación", {"fields": ("prioridad", "estado")}),
        ("Plazos", {"fields": ("fecha_emision", "fecha_limite")}),
        ("Auditoría", {"fields": ("creado_en", "actualizado_en")}),
    )

    @admin.display(description="Descripción")
    def descripcion_corta(self, obj):
        return (obj.descripcion[:60] + "...") if len(obj.descripcion) > 60 else obj.descripcion

    @admin.display(boolean=True, description="¿Vencida?")
    def esta_vencida(self, obj):
        return obj.esta_vencida

    @admin.action(description="Marcar como Vencidas las que superaron su plazo")
    def marcar_vencidas(self, request, queryset):
        hoy = timezone.localdate()
        objetivo = queryset.exclude(
            estado__in=(EstadoRecomendacion.CUMPLIDA, EstadoRecomendacion.VENCIDA)
        ).filter(fecha_limite__lt=hoy)
        actualizadas = objetivo.update(estado=EstadoRecomendacion.VENCIDA)
        self.message_user(
            request,
            f"{actualizadas} recomendación(es) marcada(s) como Vencida.",
            messages.SUCCESS,
        )


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = (
        "recomendacion",
        "tipo",
        "estado",
        "tamano_legible",
        "cargado_por",
        "creado_en",
    )
    list_filter = ("estado", "tipo", "recomendacion__estado")
    search_fields = ("recomendacion__codigo", "descripcion", "hash_archivo")
    readonly_fields = ("mime", "tamano", "hash_archivo", "anulada_en", "creado_en")
    autocomplete_fields = ("recomendacion",)
    date_hierarchy = "creado_en"
    actions = ("anular_evidencias",)

    fieldsets = (
        ("Vinculación", {"fields": ("recomendacion", "descripcion")}),
        ("Archivo", {"fields": ("archivo", "tipo", "mime", "tamano", "hash_archivo")}),
        ("Estado", {"fields": ("estado", "motivo_anulacion", "anulada_en")}),
        ("Auditoría", {"fields": ("cargado_por", "creado_en")}),
    )

    def save_model(self, request, obj, form, change):
        if not change and obj.cargado_por_id is None:
            obj.cargado_por = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Tamaño")
    def tamano_legible(self, obj):
        kb = obj.tamano / 1024
        return f"{kb:.1f} KB" if kb < 1024 else f"{kb / 1024:.1f} MB"

    @admin.action(description="Anular evidencias seleccionadas (conserva el registro)")
    def anular_evidencias(self, request, queryset):
        anuladas = 0
        for evidencia in queryset.filter(estado="VIGENTE"):
            evidencia.anular(motivo="Anulación desde el panel de administración.")
            anuladas += 1
        self.message_user(
            request,
            f"{anuladas} evidencia(s) anulada(s). El registro se conserva para trazabilidad.",
            messages.SUCCESS,
        )
