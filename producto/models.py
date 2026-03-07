from django.db import models


CATEGORIA_PRODUCTO = [
    ("chocolates", "Chocolates"),
    ("globos", "Globos"),
    ("tarjetas", "Tarjetas"),
    ("peluches", "Peluches"),
    ("vinos", "Vinos"),
    ("dulces", "Dulces"),
    ("cajas_regalo", "Cajas de regalo"),
    ("decoraciones", "Decoraciones"),
    ("velas", "Velas aromaticas"),
    ("otros", "Otros"),
]


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=500, blank=True, default="Sin descripcion")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=0)
    tipo_producto = models.CharField(max_length=30, choices=CATEGORIA_PRODUCTO, default="otros")
    imagen = models.ImageField(upload_to='productos_fotos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not (self.descripcion or "").strip():
            self.descripcion = "Sin descripcion"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

# Create your models here.
