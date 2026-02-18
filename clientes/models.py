from django.db import models


class Cliente(models.Model):
    """Modelo para clientes de la floristería."""

    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('TI', 'Tarjeta de identidad'),
        ('CE', 'Cédula de extranjería'),
        ('NIT', 'NIT'),
        ('PAS', 'Pasaporte'),
    ]

    id = models.BigAutoField(primary_key=True)
    documento = models.CharField('Documento', max_length=20, unique=True)
    tipo_documento = models.CharField(
        'Tipo de documento',
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES
    )
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    correo_electronico = models.EmailField('Correo electrónico', max_length=100, blank=True, null=True)
    direccion = models.CharField('Dirección', max_length=255, blank=True, null=True)
    ciudad = models.CharField('Ciudad', max_length=100, blank=True, null=True)
    departamento = models.CharField('Departamento', max_length=45, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.documento})"
