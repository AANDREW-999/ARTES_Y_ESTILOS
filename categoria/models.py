from django.db import models


class Categoria(models.Model):
	nombre = models.CharField(max_length=100, unique=True)
	descripcion = models.TextField(max_length=300, blank=True)
	imagen = models.ImageField(upload_to='categorias/', null=True, blank=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name = 'Categoría'
		verbose_name_plural = 'Categorías'
