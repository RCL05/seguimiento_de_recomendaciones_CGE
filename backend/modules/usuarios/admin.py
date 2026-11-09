from django.contrib import admin

from backend.modules.usuarios.models import UnidadOrganica, Usuario


@admin.register(UnidadOrganica)
class UnidadOrganicaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "padre", "activo")
    list_filter = ("activo",)
    search_fields = ("codigo", "nombre")
    ordering = ("codigo",)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("correo_institucional", "nombres", "rol", "unidad_org", "activo")
    list_filter = ("rol", "activo", "unidad_org")
    search_fields = ("correo_institucional", "nombres", "unidad_org__nombre")
    ordering = ("correo_institucional",)
