from django.db import models


TIPO_FLORES = [
    ("rosa", "Rosas"),
    ("tulipan", "Tulipanes"),
    ("girasol", "Girasoles"),
    ("orquidea", "Orquideas"),
    ("lirio", "Lirios"),
    ("clavel", "Claveles"),
    ("margarita", "Margaritas"),
    ("hortensia", "Hortensias"),
    ("mixtas", "Flores Mixtas"),
    ("otras", "Otras"),
]


class Flor(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500, blank=True, default="Sin descripcion")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=0)
    tipo_flor = models.CharField(max_length=20, choices=TIPO_FLORES, default="otras")
    imagen = models.ImageField(upload_to='flores_fotos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not (self.descripcion or "").strip():
            self.descripcion = "Sin descripcion"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

# Create your models here.
