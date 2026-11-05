from django.contrib import admin

from backend.core.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp_utc", "usuario", "modulo", "accion", "entidad", "entidad_id", "resultado")
    list_filter = ("modulo", "accion", "entidad", "resultado", "timestamp_utc")
    search_fields = ("request_id", "entidad_id", "usuario__correo_institucional", "accion", "entidad")
    date_hierarchy = "timestamp_utc"
    readonly_fields = tuple(field.name for field in AuditLog._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
