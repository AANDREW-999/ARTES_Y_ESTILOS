from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'documento', 'tipo_documento', 'nombre', 'apellido', 'correo_electronico', 'telefono', 'ciudad_id', 'departamento')
    search_fields = ('documento', 'nombre', 'apellido', 'correo_electronico')
    list_filter = ('tipo_documento', 'departamento')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
