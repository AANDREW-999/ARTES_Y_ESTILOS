from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado para autenticación.
    Solo contiene campos esenciales para login/auth.
    Los datos adicionales están en el modelo Perfil (relación 1:1)
    """
    # Documento de 10 dígitos, único (requerido para registro)
    documento = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r"^\d{10}$", message="El documento debe tener exactamente 10 dígitos.")],
        help_text="Documento de identidad (10 dígitos)"
    )

    # Email único (requerido para registro)
    email = models.EmailField('correo electrónico', unique=True, blank=True, default='')

    # Usamos first_name y last_name de Django (no duplicamos campos)
    # first_name y last_name ya están en AbstractUser

    def __str__(self):
        nombre_completo = f"{self.first_name} {self.last_name}".strip()
        return nombre_completo or self.username or self.documento

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Perfil(models.Model):
    """
    Perfil de usuario con información adicional.
    Relación 1:1 con Usuario.
    Se crea automáticamente al crear un usuario.
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')

    # Información de contacto
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=255, blank=True, verbose_name='Dirección')

    # Información personal
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True, verbose_name='Foto de perfil')

    # Campos adicionales opcionales (por si los necesitas después)
    biografia = models.TextField(blank=True, verbose_name='Biografía')

    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'


# Signal para crear automáticamente el perfil cuando se crea un usuario
@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea un perfil automáticamente cuando se crea un nuevo usuario"""
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=Usuario)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guarda el perfil cuando se guarda el usuario"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


