from django.db import models


class Categoria(models.Model):
	nombre = models.CharField(max_length=100, unique=True)
	descripcion = models.TextField(max_length=300, blank=True)
	activa = models.BooleanField(default=True)

	def __str__(self):
		return self.nombre

# Create your models here.
