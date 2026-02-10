from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class Usuario(AbstractUser):
    # Documento de 10 dígitos, único
    documento = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r"^\d{10}$", message="El documento debe tener exactamente 10 dígitos.")],
        help_text="Documento de identidad (10 dígitos)"
    )

    # Campos adicionales
    nombre = models.CharField(max_length=150, blank=True)
    apellido = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)

    # Preferimos email único para evitar confusiones en login opcional por email
    email = models.EmailField('correo electrónico', unique=True, blank=True, null=True)

    def __str__(self):
        return self.username or self.documento

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
