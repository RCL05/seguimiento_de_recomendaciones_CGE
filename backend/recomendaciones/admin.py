from django.contrib import admin, messages
from django.utils import timezone

from .models import (
    Asignacion,
    EstadoRecomendacion,
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
    inlines = (AsignacionInline,)
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
