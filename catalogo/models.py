from django.db import models

class Producto(models.Model):
    CATEGORIAS = [
        ('arreglos', '1. Arreglos florales'),
        ('ocasiones', '2. Ocasiones especiales'),
        ('condolencias', '3. Condolencias y homenajes'),
        ('tipo', '4. Flores por tipo'),
        ('plantas', '5. Plantas'),
        ('detalles', '6. Detalles y complementos'),
        ('eventos', '7. Eventos'),
    ]

    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    precio = models.DecimalField(max_digits=10, decimal_places=3)
    tamano = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True, null=True)
    
    imagen = models.ImageField(upload_to='catalogo/productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
      
        verbose_name = "Producto del Catálogo"
        verbose_name_plural = "Productos del Catálogo"