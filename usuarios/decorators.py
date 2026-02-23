"""
Decoradores personalizados para control de acceso en el panel administrativo.

Arquitectura de permisos:
- SuperAdmin (is_superuser=True): Acceso total, incluyendo gestión de usuarios
- Admin (is_staff=True pero is_superuser=False): Solo dashboard y su perfil
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def superadmin_required(view_func):
    """
    Decorador para restringir acceso solo a superadmins.
    """
    @wraps(view_func)
    @login_required(login_url='/panel/login/')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(
                request,
                '⛔ Acceso denegado. Esta funcionalidad es exclusiva para superadministradores.',
                extra_tags='level-error field-general'
            )
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def panel_login_required(view_func):
    """
    Decorador para proteger todas las vistas del panel.
    """
    @wraps(view_func)
    @login_required(login_url='/panel/login/')
    def _wrapped_view(request, *args, **kwargs):
        # El usuario ya está autenticado gracias a @login_required
        # Verificamos que tenga acceso al panel (is_staff)
        if not request.user.is_staff:
            messages.warning(
                request,
                '⚠️ No tienes permisos para acceder al panel administrativo.',
                extra_tags='level-warning field-general'
            )
            return redirect('core:index')  # Redirigir al sitio público
        return view_func(request, *args, **kwargs)
    return _wrapped_view

