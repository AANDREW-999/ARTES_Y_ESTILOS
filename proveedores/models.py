from django.db import models

class Proveedor(models.Model):
    TIPO_DOCUMENTO = [
        ('CC', 'Cédula'),
        ('NIT', 'NIT'),
        ('CE', 'Cédula Extranjería'),
    ]

    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOCUMENTO)
    numero_documento = models.CharField(max_length=50, unique=True)
    nombre_proveedor = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    correo_electronico = models.EmailField()
    ciudad = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_proveedor
