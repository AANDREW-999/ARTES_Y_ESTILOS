from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Perfil


class PerfilInline(admin.StackedInline):
    """Inline para editar el perfil junto con el usuario"""
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('telefono', 'direccion', 'fecha_nacimiento', 'foto_perfil', 'biografia')


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para el modelo Usuario"""
    inlines = (PerfilInline,)

    list_display = (
        'username', 'documento', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'date_joined'
    )

    list_filter = ('is_staff', 'is_active', 'date_joined')

    search_fields = ('documento', 'username', 'first_name', 'last_name', 'email')

    ordering = ('-date_joined',)

    # Agregar documento a los fieldsets de UserAdmin
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('documento',)}),
    )

    # Agregar documento al formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {'fields': ('documento', 'email', 'first_name', 'last_name')}),
    )


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Admin para ver perfiles independientemente"""
    list_display = ('usuario', 'telefono', 'fecha_nacimiento', 'fecha_actualizacion')
    search_fields = ('usuario__username', 'usuario__documento', 'telefono')
    list_filter = ('fecha_creacion', 'fecha_actualizacion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
