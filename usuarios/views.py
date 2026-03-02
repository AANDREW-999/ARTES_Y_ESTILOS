from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .forms import RegistroForm, LoginForm, EditarPerfilForm
from .utils import build_login_message
from .decorators import panel_login_required, superadmin_required

User = get_user_model()


# =====================================================
# 📝 REGISTRO
# =====================================================

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                usuario = form.save(commit=False)
                usuario.is_staff  = True
                usuario.is_active = True
                usuario.save()  # dispara señal post_save → crea Perfil

                perfil = usuario.perfil
                perfil.telefono         = form.cleaned_data.get('telefono', '')
                perfil.direccion        = form.cleaned_data.get('direccion', '')
                perfil.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
                perfil.biografia        = form.cleaned_data.get('biografia', '')

                foto = form.cleaned_data.get('foto_perfil')
                if foto:
                    perfil.foto_perfil = foto

                perfil.save()

                messages.success(
                    request,
                    f'¡Cuenta creada exitosamente! Bienvenid@ {usuario.first_name} {usuario.last_name}.',
                    extra_tags='level-success field-general'
                )
                return redirect('usuarios:login')

            except Exception as e:
                messages.error(
                    request,
                    f'Error al crear la cuenta: {str(e)}',
                    extra_tags='level-error field-general'
                )
        else:
            error_mostrado = False

            if 'documento' in form.errors:
                messages.error(
                    request,
                    f'El documento {request.POST.get("documento", "")} ya está registrado. Si olvidaste tu contraseña, usa la opción de recuperación.',
                    extra_tags='level-error field-documento'
                )
                error_mostrado = True

            if 'email' in form.errors:
                messages.error(
                    request,
                    f'El correo electrónico {request.POST.get("email", "")} ya está registrado. Intenta con otro email.',
                    extra_tags='level-error field-email'
                )
                error_mostrado = True

            if 'username' in form.errors:
                messages.error(
                    request,
                    f'El nombre de usuario "{request.POST.get("username", "")}" ya está en uso. Elige otro nombre de usuario.',
                    extra_tags='level-error field-username'
                )
                error_mostrado = True

            if not error_mostrado:
                messages.warning(
                    request,
                    'Revisa los campos marcados en rojo y corrige los errores.',
                    extra_tags='level-warning field-general'
                )
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


# =====================================================
# 🔐 AUTENTICACIÓN
# =====================================================

def login_view(request):
    """
    Vista de login para el panel administrativo.
    Solo permite acceso a usuarios con is_staff=True.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('core:dashboard')
        else:
            messages.warning(
                request,
                'No tienes permisos para acceder al panel administrativo.',
                extra_tags='level-warning field-general'
            )
            auth_logout(request)
            return redirect('core:landing')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                messages.error(
                    request,
                    '⛔ Acceso denegado. No tienes permisos para acceder al panel administrativo.',
                    extra_tags='level-error field-general'
                )
                return render(request, 'usuarios/login.html', {'form': form})
            auth_login(request, user)
            messages.success(
                request,
                f'¡Bienvenid@ de nuevo, {user.first_name}! Has iniciado sesión correctamente.',
                extra_tags='level-success field-general'
            )
            return redirect('core:dashboard')
        else:
            usuario_o_documento = request.POST.get('username')
            msg = build_login_message(form, usuario_o_documento=usuario_o_documento)
            messages.error(request, msg['text'], extra_tags=msg['tags'])
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """Cierra la sesión y redirige al inicio"""
    auth_logout(request)
    messages.success(
        request,
        'Sesión cerrada correctamente. ¡Hasta pronto!',
        extra_tags='level-success field-general'
    )
    return redirect('core:landing')


# =====================================================
# 👤 GESTIÓN DE PERFIL PERSONAL
# =====================================================

@panel_login_required
def perfil_view(request):
    return render(request, 'usuarios/perfil.html')


@panel_login_required
def editar_perfil_view(request):
    """
    Vista para que el usuario edite su propio perfil.

    FIX REDIRECCIÓN: en éxito redirige a 'usuarios:perfil' (solo lectura)
    en lugar de 'usuarios:editar_perfil' (misma página de edición).
    Esto da confirmación visual clara: el usuario ve su perfil actualizado
    en lugar de quedar en el formulario vacío de nuevo.

    NOTA: EditarPerfilForm recibe editing_user=request.user,
    lo que activa el pop() de is_active/is_staff/is_superuser en __init__,
    evitando que esos campos sean procesados como False en el POST.
    """
    usuario = request.user

    if request.method == 'POST':
        form = EditarPerfilForm(
            request.POST,
            request.FILES,
            instance=usuario,
            editing_user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                '✅ Tu perfil ha sido actualizado correctamente.',
                extra_tags='level-success field-general'
            )
            # FIX: redirigir a vista de solo lectura para confirmar el cambio
            return redirect('usuarios:perfil')
        else:
            messages.warning(
                request,
                '⚠️ Revisa los campos resaltados y corrige los errores.',
                extra_tags='level-warning field-general'
            )
    else:
        form = EditarPerfilForm(
            instance=usuario,
            editing_user=request.user
        )

    return render(request, 'usuarios/editar_perfil.html', {
        'form':    form,
        'usuario': usuario,
        'perfil':  usuario.perfil,
    })


# =====================================================
# 🔧 RECUPERACIÓN DE CONTRASEÑA
# =====================================================

class RecuperarPasswordView(PasswordResetView):
    """
    Vista personalizada para recuperación de contraseña del panel.
    Envía correos en formato HTML con diseño floral elegante.
    """
    template_name            = 'recuperar_password/solicitar_password.html'
    email_template_name      = 'recuperar_password/email_recuperar_password.txt'
    html_email_template_name = 'recuperar_password/email_recuperar_password.html'
    subject_template_name    = 'recuperar_password/asunto_recuperar_password.txt'
    success_url              = reverse_lazy('usuarios:password_reset_done')

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject   = render_to_string(subject_template_name, context)
        subject   = ''.join(subject.splitlines())
        body_text = render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[to_email]
        )

        if html_email_template_name:
            body_html = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(body_html, "text/html")

        email_message.send(fail_silently=False)


class RecuperarPasswordHechoView(PasswordResetDoneView):
    template_name = 'recuperar_password/solicitud_enviada.html'

class RestablecerPasswordConfirmarView(PasswordResetConfirmView):
    template_name    = 'recuperar_password/confirmar_password.html'
    success_url      = reverse_lazy('usuarios:password_reset_complete')

class RestablecerPasswordCompletoView(PasswordResetCompleteView):
    template_name = 'recuperar_password/password_actualizada.html'


# =====================================================
# 👥 GESTIÓN DE USUARIOS
# =====================================================

@login_required
def lista_usuarios_view(request):
    """
    Lista todos los usuarios del sistema.
    El usuario en sesión se muestra separado en "Mi Usuario".
    Los demás en "Otros Usuarios" (solo lectura para no-superadmins).
    """
    usuario_actual = request.user
    otros_usuarios = User.objects.exclude(id=usuario_actual.id).select_related('perfil').order_by('-date_joined')

    context = {
        'usuario_actual':    usuario_actual,
        'otros_usuarios':    otros_usuarios,
        'total_usuarios':    User.objects.count(),
        'usuarios_activos':  User.objects.filter(is_active=True).count(),
        'superadmins':       User.objects.filter(is_superuser=True).count(),
        'admins':            User.objects.filter(is_staff=True, is_superuser=False).count(),
        'usuarios_normales': User.objects.filter(is_staff=False).count(),
    }
    return render(request, 'usuarios/lista_usuarios.html', context)


@superadmin_required
def crear_usuario_view(request):
    """
    Crea un nuevo usuario en el sistema.
    Solo accesible para superadmins.
    """
    if request.method == 'POST':
        post_data    = request.POST.copy()
        is_active    = request.POST.get('is_active')    == 'on'
        is_staff     = request.POST.get('is_staff')     == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'

        form = RegistroForm(post_data, request.FILES)

        if form.is_valid():
            try:
                usuario              = form.save(commit=False)
                usuario.is_staff     = is_staff
                usuario.is_active    = is_active
                usuario.is_superuser = is_superuser
                usuario.save()

                perfil = usuario.perfil
                perfil.telefono         = form.cleaned_data.get('telefono', '')
                perfil.direccion        = form.cleaned_data.get('direccion', '')
                perfil.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
                perfil.biografia        = form.cleaned_data.get('biografia', '')

                foto = form.cleaned_data.get('foto_perfil')
                if foto:
                    perfil.foto_perfil = foto

                perfil.save()

                messages.success(
                    request,
                    f'✅ Usuario <strong>{usuario.username}</strong> creado correctamente.',
                    extra_tags='level-success field-general'
                )
                return redirect('usuarios:lista_usuarios')

            except Exception as e:
                messages.error(
                    request,
                    f'❌ Error al crear usuario: {str(e)}',
                    extra_tags='level-error field-general'
                )
        else:
            error_mostrado = False

            if 'documento' in form.errors:
                messages.error(request,
                    f'El documento {request.POST.get("documento", "")} ya está registrado.',
                    extra_tags='level-error field-documento')
                error_mostrado = True

            if 'email' in form.errors:
                messages.error(request,
                    f'El correo electrónico {request.POST.get("email", "")} ya está registrado.',
                    extra_tags='level-error field-email')
                error_mostrado = True

            if 'username' in form.errors:
                messages.error(request,
                    f'El nombre de usuario "{request.POST.get("username", "")}" ya está en uso.',
                    extra_tags='level-error field-username')
                error_mostrado = True

            if not error_mostrado:
                messages.warning(request,
                    '⚠️ Revisa los campos resaltados y corrige los errores.',
                    extra_tags='level-warning field-general')

    else:
        form         = RegistroForm()
        is_active    = True
        is_staff     = False
        is_superuser = False

    context = {
        'form':          form,
        'titulo':        'Crear Nuevo Usuario',
        'boton_texto':   'Crear Usuario',
        'is_active':     is_active if request.method == 'POST' else True,
        'is_staff':      is_staff  if request.method == 'POST' else False,
        'is_superuser':  is_superuser if request.method == 'POST' else False,
    }
    return render(request, 'usuarios/crear_usuario.html', context)


@login_required
def editar_usuario_view(request, user_id):
    """
    Edita un usuario existente.
    Un usuario SOLO puede editar su propio perfil.
    """
    usuario = get_object_or_404(User, id=user_id)

    if usuario.id != request.user.id:
        messages.error(
            request,
            '⛔ No tienes permiso para editar este usuario. Solo puedes editar tu propio perfil.',
            extra_tags='level-error field-general'
        )
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        documento_original = usuario.documento
        documento_nuevo    = request.POST.get('documento', '')

        if documento_original != documento_nuevo:
            confirmar = request.POST.get('confirmar_cambio_documento', '')
            if confirmar != 'CONFIRMAR':
                messages.error(
                    request,
                    '⚠️ Para cambiar el documento debes marcar la casilla de confirmación y escribir "CONFIRMAR" en el campo.',
                    extra_tags='level-error field-documento'
                )
                form = EditarPerfilForm(request.POST, request.FILES, instance=usuario, editing_user=request.user)
                return render(request, 'usuarios/editar_usuario.html', {
                    'form': form, 'usuario': usuario,
                    'es_auto_edicion': True,
                    'titulo': 'Editar Mi Perfil',
                    'boton_texto': 'Guardar Cambios',
                    'documento_original': documento_original,
                })

        form = EditarPerfilForm(
            request.POST,
            request.FILES,
            instance=usuario,
            editing_user=request.user
        )

        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    '✅ Tu perfil ha sido actualizado correctamente.',
                    extra_tags='level-success field-general'
                )
                return redirect('usuarios:perfil')
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Error al actualizar perfil: {str(e)}',
                    extra_tags='level-error field-general'
                )
        else:
            messages.warning(
                request,
                '⚠️ Revisa los campos resaltados y corrige los errores.',
                extra_tags='level-warning field-general'
            )
    else:
        form = EditarPerfilForm(instance=usuario, editing_user=request.user)

    return render(request, 'usuarios/editar_usuario.html', {
        'form':               form,
        'usuario':            usuario,
        'es_auto_edicion':    True,
        'titulo':             'Editar Mi Perfil',
        'boton_texto':        'Guardar Cambios',
        'documento_original': usuario.documento,
    })


@superadmin_required
def desactivar_usuario_view(request, user_id):
    """
    Desactiva un usuario sin eliminarlo (soft-delete).
    Solo accesible para superadmins.
    """
    usuario = get_object_or_404(User, id=user_id)

    if usuario.id == request.user.id:
        messages.error(request, '⛔ No puedes desactivar tu propia cuenta.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if usuario.is_superuser:
        messages.error(request,
            '⛔ No puedes desactivar a un superadministrador. '
            'Primero debes quitarle el rol de superadmin desde edición.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()
        messages.success(request,
            f'✅ Usuario <strong>{usuario.username}</strong> desactivado correctamente.',
            extra_tags='level-success field-general')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/desactivar_usuario.html', {'usuario': usuario})


@login_required
def visualizar_usuario_view(request, user_id):
    usuario = get_object_or_404(User.objects.select_related('perfil'), id=user_id)
    return render(request, 'usuarios/visualizar_usuario.html', {
        'usuario':          usuario,
        'perfil':           usuario.perfil,
        'es_propio_perfil': usuario.id == request.user.id,
    })


@superadmin_required
def activar_usuario_view(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        usuario.is_active = True
        usuario.save()
        messages.success(request,
            f'✅ Usuario <strong>{usuario.username}</strong> activado correctamente.',
            extra_tags='level-success field-general')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/activar_usuario.html', {'usuario': usuario})


@login_required
def eliminar_usuario_view(request, user_id):
    """
    Elimina PERMANENTEMENTE una cuenta.
    Un usuario SOLO puede eliminar su propia cuenta.
    """
    usuario = get_object_or_404(User, id=user_id)

    if usuario.id != request.user.id:
        messages.error(request,
            '⛔ No tienes permiso para eliminar este usuario. Solo puedes eliminar tu propia cuenta.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        if request.POST.get('confirmar_eliminacion') == 'ELIMINAR':
            username = usuario.username
            auth_logout(request)
            usuario.delete()
            messages.warning(request,
                f'⚠️ Tu cuenta <strong>{username}</strong> ha sido eliminada permanentemente.',
                extra_tags='level-warning field-general')
            return redirect('core:index')
        else:
            messages.error(request,
                '⛔ Debes escribir "ELIMINAR" para confirmar esta acción.',
                extra_tags='level-error field-general')

    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})