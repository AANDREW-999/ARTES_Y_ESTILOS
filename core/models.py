from django.db import models


class Notificacion(models.Model):
	CATEGORIA_CHOICES = [
		("movimiento", "Movimiento"),
		("stock", "Stock"),
		("cuenta", "Cuenta"),
	]

	NIVEL_STOCK_CHOICES = [
		("agotado", "Agotado"),
		("bajo", "Bajo"),
		("medio", "Medio"),
		("alto", "Alto"),
	]

	ESTILO_CHOICES = [
		("success", "Success"),
		("info", "Info"),
		("warning", "Warning"),
		("error", "Error"),
	]

	categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
	estilo = models.CharField(max_length=20, choices=ESTILO_CHOICES, default="info")
	titulo = models.CharField(max_length=120)
	mensaje = models.CharField(max_length=255)
	nivel_stock = models.CharField(max_length=20, choices=NIVEL_STOCK_CHOICES, blank=True)
	leida = models.BooleanField(default=False)
	creada_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-creada_en"]

	def __str__(self):
		return f"{self.titulo} - {self.creada_en:%Y-%m-%d %H:%M}"
