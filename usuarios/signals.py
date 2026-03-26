import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


@receiver(post_migrate)
def crear_superadmin(sender, **kwargs):
    if not User.objects.filter(is_superuser=True).exists():
        print("⚠️ No existe superusuario. Creando superadmin por defecto...")

        username = config('DJANGO_SUPERUSER_USERNAME')
        email = config('DJANGO_SUPERUSER_EMAIL')
        password = config('DJANGO_SUPERUSER_PASSWORD')
        documento = config('DJANGO_SUPERUSER_DOCUMENTO')

        # 🔒 Validación de seguridad
        if not all([username, email, password, documento]):
            print("❌ Variables de entorno incompletas para crear superadmin")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            documento=documento
        )

        print(f"✅ Superadmin creado correctamente: {username}")