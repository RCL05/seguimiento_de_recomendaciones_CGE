from django.contrib import admin
from django.urls import path

admin.site.site_header = "Seguimiento de Recomendaciones CGE - UNL"
admin.site.site_title = "Recomendaciones CGE"
admin.site.index_title = "Panel de Administración"

urlpatterns = [
    path("admin/", admin.site.urls),
]
