from django.contrib import admin

from backend.modules.recomendaciones.models import Evidencia, InformeCGE, PlanAccion, Recomendacion


@admin.register(InformeCGE)
class InformeCGEAdmin(admin.ModelAdmin):
    list_display = ("numero_informe", "periodo_auditado", "fecha_notificacion", "creado_por", "creado_en")
    list_filter = ("fecha_notificacion", "creado_en")
    search_fields = ("numero_informe", "periodo_auditado")
    date_hierarchy = "fecha_notificacion"


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ("numero_recomendacion", "informe", "unidad_responsable", "estado", "prioridad", "fecha_vencimiento_legal")
    list_filter = ("estado", "prioridad", "fecha_vencimiento_legal", "creada_en", "unidad_responsable")
    search_fields = ("numero_recomendacion", "descripcion", "informe__numero_informe", "unidad_responsable__nombre")
    date_hierarchy = "fecha_vencimiento_legal"
    list_select_related = ("informe", "unidad_responsable")


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ("nombre_archivo", "recomendacion", "tipo", "estado", "validada", "fecha_carga", "subido_por")
    list_filter = ("tipo", "estado", "validada", "fecha_carga")
    search_fields = ("nombre_archivo", "hash_sha256", "recomendacion__numero_recomendacion")
    date_hierarchy = "fecha_carga"
    readonly_fields = ("hash_sha256", "fecha_carga", "inmutable")


@admin.register(PlanAccion)
class PlanAccionAdmin(admin.ModelAdmin):
    list_display = ("recomendacion", "descripcion_hito", "fecha_compromiso", "completado", "creado_por")
    list_filter = ("completado", "fecha_compromiso")
    search_fields = ("descripcion_hito", "recomendacion__numero_recomendacion")
    date_hierarchy = "fecha_compromiso"
