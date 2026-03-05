from django.db import models


class Producto(models.Model):
	nombre = models.CharField(max_length=120)
	descripcion = models.TextField(max_length=500)
	precio = models.DecimalField(max_digits=10, decimal_places=2)
	imagen = models.ImageField(upload_to='productos_fotos/', blank=True, null=True)

	def __str__(self):
		return self.nombre

# Create your models here.
