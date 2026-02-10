from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import get_user_model

from .forms import RegistroForm, LoginForm

User = get_user_model()

# Registro
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            cleaned = form.cleaned_data
            if not usuario.first_name and cleaned.get('nombre'):
                usuario.first_name = cleaned['nombre']
            if not usuario.last_name and cleaned.get('apellido'):
                usuario.last_name = cleaned['apellido']
            # Dar acceso al panel base
            usuario.is_staff = True
            usuario.is_active = True
            usuario.save()
            messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
        else:
            # Mostrar errores detallados
            messages.error(request, 'Hay errores en el formulario, por favor corrige los campos marcados.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Has iniciado sesión correctamente.')
            return redirect('core:dashboard')
        else:
            # Mostrar errores precisos de autenticación
            if form.non_field_errors():
                for err in form.non_field_errors():
                    messages.error(request, err)
            else:
                messages.error(request, 'Credenciales inválidas, intenta nuevamente.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')

# Logout
def logout_view(request):
    auth_logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('core:index')

# Recuperación de contraseña
class RecuperarPasswordView(PasswordResetView):
    template_name = 'recuperar_password/solicitar_password.html'
    email_template_name = 'recuperar_password/email_recuperar_password.txt'
    subject_template_name = 'recuperar_password/asunto_recuperar_password.txt'
    success_url = reverse_lazy('usuarios:password_reset_done')

class RecuperarPasswordHechoView(PasswordResetDoneView):
    template_name = 'recuperar_password/solicitud_enviada.html'

class RestablecerPasswordConfirmarView(PasswordResetConfirmView):
    template_name = 'recuperar_password/confirmar_password.html'
    success_url = reverse_lazy('usuarios:password_reset_complete')

class RestablecerPasswordCompletoView(PasswordResetCompleteView):
    template_name = 'recuperar_password/password_actualizada.html'

# Panel de administración de usuarios (placeholders)
@login_required
def lista_usuarios_view(request):
    usuarios = User.objects.all().order_by('documento')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def crear_usuario_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_staff = True
            usuario.is_active = True
            usuario.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.error(request, 'Hay errores en el formulario, corrígelos.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

@login_required
def editar_usuario_view(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.error(request, 'Hay errores en el formulario, corrígelos.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
def eliminar_usuario_view(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        usuario.delete()
        messages.info(request, 'Usuario eliminado.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})
