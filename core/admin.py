from django.contrib import admin

from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
	list_display = ("titulo", "categoria", "estilo", "nivel_stock", "leida", "creada_en")
	list_filter = ("categoria", "estilo", "nivel_stock", "leida")
	search_fields = ("titulo", "mensaje")

# Register your models here.
