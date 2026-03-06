from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=150)

    categoria = models.ForeignKey(
        'categoria.Categoria',
        on_delete=models.PROTECT,
        related_name='productos',
    )
    precio = models.DecimalField(max_digits=10, decimal_places=3)
    tamano = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True, null=True)

    activo = models.BooleanField(default=True)
    
    imagen = models.ImageField(upload_to='catalogo/productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
      
        verbose_name = "Producto del Catálogo"
        verbose_name_plural = "Productos del Catálogo"