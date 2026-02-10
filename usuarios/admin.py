from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'documento', 'username', 'first_name', 'last_name', 'email',
        'nombre', 'apellido', 'telefono', 'direccion', 'fecha_nacimiento', 'is_staff', 'is_active'
    )
    search_fields = ('documento', 'username', 'first_name', 'last_name', 'email', 'telefono')
    list_filter = ('is_staff', 'is_active')
