from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.db import transaction
from .forms import LoginForm, RegistroForm, EditarUsuarioForm, EditarPerfilForm


# ==================== VISTAS DE AUTENTICACIÓN ====================

@csrf_protect
@never_cache
def login_view(request):
    """
    Vista para el inicio de sesión de usuarios
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)

                    if not remember_me:
                        request.session.set_expiry(0)

                    messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')

                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    elif user.is_staff:
                        return redirect('core:dashboard')
                    else:
                        return redirect('core:index')
                else:
                    messages.error(request, 'Esta cuenta ha sido desactivada.')
            else:
                messages.error(request, 'Documento o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor completa todos los campos correctamente.')

        # IMPORTANTE: Si llegamos aquí, hay errores
        # Verificar si la petición vino del modal (tiene la URL de index)
        referer = request.META.get('HTTP_REFERER', '')
        if 'auth/login' not in referer:  # Viene del modal en index
            return redirect('core:index')

    # GET request - mostrar formulario normal
    form = LoginForm()
    context = {'form': form, 'titulo': 'Iniciar Sesión'}
    return render(request, 'usuarios/login.html', context)


@csrf_protect
def registro_view(request):
    """
    Vista para el registro de nuevos usuarios
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    # asegurar usuario activo
                    if not user.is_active:
                        user.is_active = True
                        user.save(update_fields=['is_active'])
                messages.success(
                    request,
                    f'Cuenta creada exitosamente para {user.get_full_name()}. Ya puedes iniciar sesión.'
                )
                # Respuesta AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'ok': True,
                        'message': 'Usuario registrado correctamente. Redirigiendo al inicio de sesión…',
                        'redirect_to': reverse_lazy('usuarios:login')
                    })
                return redirect('usuarios:login')
            except Exception as e:
                messages.error(request, 'Ocurrió un error al registrar el usuario. Inténtalo de nuevo.')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({'ok': False, 'detail': 'Error interno al registrar.'}, status=500)
        else:
            # Respuesta AJAX con errores
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse(form.errors, status=400)
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()

    context = {
        'form': form,
        'titulo': 'Registro de Usuario'
    }
    return render(request, 'usuarios/registro.html', context)


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:index')


# ==================== RECUPERACIÓN DE PASSWORD (CBVs) ====================

class RecuperarPasswordView(auth_views.PasswordResetView):
    template_name = 'recuperar_password/solicitar_password.html'
    email_template_name = 'recuperar_password/email_recuperar_password.txt'
    subject_template_name = 'recuperar_password/asunto_recuperar_password.txt'
    success_url = reverse_lazy('usuarios:password_reset_done')


class RecuperarPasswordHechoView(auth_views.PasswordResetDoneView):
    template_name = 'recuperar_password/solicitud_enviada.html'


class RestablecerPasswordConfirmarView(auth_views.PasswordResetConfirmView):
    template_name = 'recuperar_password/confirmar_password.html'
    success_url = reverse_lazy('usuarios:password_reset_complete')


class RestablecerPasswordCompletoView(auth_views.PasswordResetCompleteView):
    template_name = 'recuperar_password/password_actualizada.html'


# ==================== PANEL DE ADMINISTRACIÓN ====================

def es_staff(user):
    """Función auxiliar para verificar si el usuario es staff"""
    return user.is_staff


@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def lista_usuarios_view(request):
    """
    Vista para listar todos los usuarios
    """
    # Obtener parámetros de búsqueda y filtrado
    busqueda = request.GET.get('buscar', '')
    filtro_activo = request.GET.get('activo', '')
    filtro_staff = request.GET.get('staff', '')

    # Query base
    usuarios = User.objects.select_related('perfil').all()

    # Aplicar filtros
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(perfil__documento__icontains=busqueda)
        )

    if filtro_activo:
        usuarios = usuarios.filter(is_active=filtro_activo == 'true')

    if filtro_staff:
        usuarios = usuarios.filter(is_staff=filtro_staff == 'true')

    # Ordenar
    usuarios = usuarios.order_by('-date_joined')

    context = {
        'titulo': 'Gestión de Usuarios',
        'usuarios': usuarios,
        'busqueda': busqueda,
        'filtro_activo': filtro_activo,
        'filtro_staff': filtro_staff,
    }
    return render(request, 'usuarios/lista_usuarios.html', context)


@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def crear_usuario_view(request):
    """
    Vista para crear un nuevo usuario desde el panel admin
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.get_full_name()} creado exitosamente.')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()

    context = {
        'titulo': 'Crear Nuevo Usuario',
        'form': form,
        'accion': 'Crear'
    }
    return render(request, 'usuarios/crear_usuario.html', context)


@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def editar_usuario_view(request, user_id):
    """
    Vista para editar un usuario existente
    """
    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=usuario)
        form_perfil = EditarPerfilForm(request.POST, request.FILES, instance=usuario.perfil)

        if form_usuario.is_valid() and form_perfil.is_valid():
            form_usuario.save()
            form_perfil.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} actualizado exitosamente.')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form_usuario = EditarUsuarioForm(instance=usuario)
        form_perfil = EditarPerfilForm(instance=usuario.perfil)

    context = {
        'titulo': f'Editar Usuario: {usuario.get_full_name()}',
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
        'usuario': usuario,
        'accion': 'Actualizar'
    }
    return render(request, 'usuarios/editar_usuario.html', context)


@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def eliminar_usuario_view(request, user_id):
    """
    Vista para eliminar (desactivar) un usuario
    """
    usuario = get_object_or_404(User, id=user_id)

    # No permitir eliminar al superusuario
    if usuario.is_superuser:
        messages.error(request, 'No se puede eliminar un superusuario.')
        return redirect('usuarios:lista_usuarios')

    # No permitir que se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_full_name()} desactivado exitosamente.')
        return redirect('usuarios:lista_usuarios')

    context = {
        'titulo': 'Eliminar Usuario',
        'usuario': usuario
    }
    return render(request, 'usuarios/eliminar_usuario.html', context)


@login_required
def perfil_view(request):
    """
    Vista para que el usuario vea/edite su propio perfil
    """
    usuario = request.user

    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=usuario)
        form_perfil = EditarPerfilForm(request.POST, request.FILES, instance=usuario.perfil)

        if form_usuario.is_valid() and form_perfil.is_valid():
            form_usuario.save()
            form_perfil.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
    else:
        form_usuario = EditarUsuarioForm(instance=usuario)
        form_perfil = EditarPerfilForm(instance=usuario.perfil)

    context = {
        'titulo': 'Mi Perfil',
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
    }
    return render(request, 'usuarios/perfil.html', context)
