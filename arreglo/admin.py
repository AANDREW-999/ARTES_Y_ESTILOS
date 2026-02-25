from django.contrib import admin
from .models import Arreglo

@admin.register(Arreglo)
class ArregloAdmin(admin.ModelAdmin):
    # Esto muestra columnas bonitas en el listado del admin
    list_display = ('nombre_flor', 'tipo_producto', 'precio')
    search_fields = ('nombre_flor', 'tipo_producto')
# Register your models here.
