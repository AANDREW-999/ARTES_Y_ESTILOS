from django.db import models

class Arreglo(models.Model):
    # Usamos texto normal mientras las otras apps están listas
    nombre_flor = models.CharField(max_length=100, verbose_name="Flor (texto)")
    tipo_producto = models.CharField(max_length=100, verbose_name="Producto (texto)")
    
    descripcion = models.TextField(max_length=500, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    imagen = models.ImageField(upload_to='arreglos_fotos/', verbose_name="Imagen")

    def __str__(self):
        return f"{self.nombre_flor} - {self.tipo_producto}"

# Create your models here.
