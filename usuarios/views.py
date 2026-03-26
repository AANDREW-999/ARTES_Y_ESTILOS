import requests
import tempfile
from django.conf import settings
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme
from core.notifications import crear_notificacion
from django.core.cache import cache

from .forms import RegistroForm, LoginForm, EditarPerfilForm
from .utils import build_login_message, build_form_messages
from .decorators import panel_login_required, superadmin_required
from .services.backup_service import (
    BackupError,
    create_backup,
    delete_backup,
    list_backups,
    resolve_backup_path,
    restore_backup,
    validate_backup_file,
)

User = get_user_model()

def validar_recaptcha(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')

    if not recaptcha_response:
        return False

    data = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }

    r = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data=data
    )

    result = r.json()
    return result.get('success', False)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def _default_db_engine():
    return settings.DATABASES.get('default', {}).get('ENGINE', '')


def _default_db_path():
    db_name = settings.DATABASES.get('default', {}).get('NAME')
    return Path(str(db_name)).resolve()


def _safe_next_url(request):
    next_url = (request.GET.get('next') or request.POST.get('next') or '').strip()
    if not next_url:
        return ''

    if url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return ''


def _redirect_next_or(request, default_view_name: str):
    next_url = _safe_next_url(request)
    if next_url:
        return redirect(next_url)
    return redirect(default_view_name)


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

MAX_INTENTOS = settings.LOGIN_MAX_INTENTOS
TIEMPO_BLOQUEO = settings.LOGIN_TIEMPO_BLOQUEO

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

        # 🔐 CONFIGURACIÓN
        ip = get_client_ip(request)
        key = f"login_attempts_{ip}"
        intentos = cache.get(key, 0)

        CAPTCHA_DESDE_INTENTOS = 3  # 🔥 puedes mover esto a settings luego

        # 🔒 BLOQUEO TOTAL
        if intentos >= MAX_INTENTOS:
            minutos = TIEMPO_BLOQUEO // 60

            messages.error(
                request,
                f"Demasiados intentos fallidos. Intenta nuevamente en {minutos} minutos.",
                extra_tags='level-error field-general'
            )

            form = LoginForm(request, data=request.POST)
            return render(request, 'usuarios/login.html', {'form': form})

        # 🤖 CAPTCHA SOLO SI ES NECESARIO
        if intentos >= CAPTCHA_DESDE_INTENTOS:
            if not validar_recaptcha(request):
                messages.warning(
                    request,
                    "Por seguridad, verifica que no eres un robot.",
                    extra_tags='level-warning field-general'
                )
                form = LoginForm(request, data=request.POST)
                return render(request, 'usuarios/login.html', {'form': form})

        form = LoginForm(request, data=request.POST)

        # ✅ LOGIN CORRECTO
        if form.is_valid():
            user = form.get_user()

            if not user.is_staff:
                messages.error(
                    request,
                    '⛔ Acceso denegado. No tienes permisos para acceder al panel administrativo.',
                    extra_tags='level-error field-general'
                )
                return render(request, 'usuarios/login.html', {'form': form})

            # 🔥 RESET INTENTOS
            auth_login(request, user)
            cache.delete(key)

            messages.success(
                request,
                f'¡Bienvenid@ de nuevo, {user.first_name}! Has iniciado sesión correctamente.',
                extra_tags='level-success field-general'
            )
            return redirect('core:dashboard')

        # ❌ LOGIN FALLIDO
        else:
            usuario_o_documento = request.POST.get('username')
            msg = build_login_message(form, usuario_o_documento=usuario_o_documento)

            # ➕ SUMAR INTENTO
            intentos += 1
            cache.set(key, intentos, timeout=TIEMPO_BLOQUEO)

            intentos_restantes = MAX_INTENTOS - intentos

            # 🧠 MENSAJE DINÁMICO
            if intentos_restantes > 0:
                mensaje_final = f"{msg['text']} Te quedan {intentos_restantes} intento(s) antes de bloquearse."
            else:
                mensaje_final = "Has alcanzado el máximo de intentos permitidos."

            if 'field-inactive' in msg.get('tags', ''):
                auth_logout(request)
                return redirect('usuarios:panel_inactivo')

            messages.error(
                request,
                mensaje_final,
                extra_tags=msg['tags']
            )

    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def panel_inactivo_view(request):
    if not request.user.is_authenticated:
        messages.warning(
            request,
            'Tu cuenta esta inactiva. No puedes ingresar hasta que un superadministrador la active nuevamente.',
            extra_tags='level-warning field-inactive'
        )
    return render(request, 'usuarios/panel_inactivo.html')


def validar_usuario_documento_view(request):
    valor = (request.GET.get('q') or '').strip()

    if not valor:
        return JsonResponse({
            'exists': False,
            'type': 'empty',
            'message': 'Ingresa un usuario o documento.'
        })

    if valor.isdigit():
        if not (6 <= len(valor) <= 10):
            return JsonResponse({
                'exists': False,
                'type': 'documento',
                'message': 'El documento debe tener entre 6 y 10 digitos.'
            })
        exists = User.objects.filter(documento=valor).exists()
        return JsonResponse({
            'exists': exists,
            'type': 'documento',
            'message': 'Documento registrado.' if exists else 'Documento no encontrado.'
        })

    exists = User.objects.filter(username=valor).exists()
    return JsonResponse({
        'exists': exists,
        'type': 'usuario',
        'message': 'Usuario registrado.' if exists else 'Usuario no encontrado.'
    })


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

@login_required
@panel_login_required
def perfil_view(request):
    db_path = _default_db_path()
    context = {
        'db_engine': _default_db_engine(),
        'db_is_sqlite': _default_db_engine().endswith('sqlite3'),
        'db_name': db_path.name,
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
@panel_login_required
def seguridad_view(request):
    db_path = _default_db_path()
    backups = [
        {
            'nombre': item.name,
            'fecha': item.modified_at,
            'size': item.size_kb,
            'tipo': 'ZIP' if item.extension == '.zip' else 'JSON',
            'icon': 'bi-file-earmark-zip' if item.extension == '.zip' else 'bi-filetype-json',
        }
        for item in list_backups()
    ]

    context = {
        'db_engine': _default_db_engine(),
        'db_is_sqlite': _default_db_engine().endswith('sqlite3'),
        'db_name': db_path.name,
        'backups': backups,
        'auto_download_backup': request.session.pop('backup_auto_download', ''),
    }

    return render(request, 'usuarios/seguridad.html', context)


@superadmin_required
def generar_backup_db_view(request):
    if request.method != 'POST':
        return _redirect_next_or(request, 'usuarios:seguridad')

    compress = request.POST.get('compress_backup') == '1'

    try:
        backup = create_backup(compress=compress)

    except BackupError as exc:
        messages.error(
            request,
            f'No fue posible generar el backup: {exc}',
            extra_tags='level-error field-general'
        )
        return _redirect_next_or(request, 'usuarios:seguridad')

    messages.success(
        request,
        f'Backup generado correctamente: {backup.name}.',
        extra_tags='level-success field-general'
    )

    # En lugar de responder con FileResponse (que no recarga la página),
    # redirigimos para que la lista se actualice y disparamos la descarga
    # desde la vista de Seguridad (JS) una sola vez.
    request.session['backup_auto_download'] = backup.name
    return _redirect_next_or(request, 'usuarios:seguridad')


@superadmin_required
def descargar_backup_db_view(request, backup_name):
    try:
        backup_path = resolve_backup_path(backup_name)
    except BackupError as exc:
        messages.error(
            request,
            f'No se pudo descargar el backup: {exc}',
            extra_tags='level-error field-general'
        )
        return _redirect_next_or(request, 'usuarios:seguridad')

    content_type = 'application/zip' if backup_path.suffix.lower() == '.zip' else 'application/json'

    return FileResponse(
        open(backup_path, 'rb'),
        as_attachment=True,
        filename=backup_path.name,
        content_type=content_type,
    )


@superadmin_required
def eliminar_backup_db_view(request, backup_name):
    if request.method != 'POST':
        return _redirect_next_or(request, 'usuarios:seguridad')

    try:
        delete_backup(backup_name)
        messages.success(
            request,
            f'Backup eliminado: {backup_name}.',
            extra_tags='level-success field-general'
        )
    except BackupError as exc:
        messages.error(
            request,
            f'No se pudo eliminar el backup: {exc}',
            extra_tags='level-error field-general'
        )

    return _redirect_next_or(request, 'usuarios:seguridad')


@superadmin_required
def restaurar_backup_db_view(request):
    if request.method != 'POST':
        return _redirect_next_or(request, 'usuarios:seguridad')
    selected_backup = request.POST.get('backup_selected')
    uploaded_file = request.FILES.get('backup_file')

    tmp_path = None
    is_temp_upload = False

    try:
        if selected_backup:
            tmp_path = resolve_backup_path(selected_backup)

        elif uploaded_file:
            extension = Path(uploaded_file.name).suffix.lower()
            if extension not in {'.json', '.zip'}:
                messages.error(
                    request,
                    'Archivo inválido. Solo se permiten backups .json o .zip.',
                    extra_tags='level-error field-general'
                )
                return _redirect_next_or(request, 'usuarios:seguridad')

            max_upload_mb = int(getattr(settings, 'BACKUP_MAX_UPLOAD_MB', 30))
            if uploaded_file.size > max_upload_mb * 1024 * 1024:
                messages.error(
                    request,
                    f'El archivo supera el límite de {max_upload_mb} MB.',
                    extra_tags='level-error field-general'
                )
                return _redirect_next_or(request, 'usuarios:seguridad')

            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file.close()
            tmp_path = Path(tmp_file.name)
            is_temp_upload = True

        else:
            messages.warning(
                request,
                'Debes seleccionar un backup o subir un archivo.',
                extra_tags='level-warning field-general'
            )
            return _redirect_next_or(request, 'usuarios:seguridad')

        validate_backup_file(tmp_path)
        restore_backup(tmp_path)

        messages.success(
            request,
            'Backup restaurado correctamente.',
            extra_tags='level-success field-general'
        )

    except BackupError as exc:
        messages.error(
            request,
            f'Error al restaurar el backup: {exc}',
            extra_tags='level-error field-general'
        )

    finally:
        # Solo borrar si es archivo temporal
        if is_temp_upload and tmp_path and tmp_path.exists():
            tmp_path.unlink()

    return _redirect_next_or(request, 'usuarios:seguridad')


@login_required
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
@panel_login_required
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


@login_required
@panel_login_required
def crear_usuario_view(request):
    """
    Crea un nuevo usuario en el sistema.
    Accesible para usuarios del panel (staff).
    Solo superadmins pueden asignar rol de superadministrador.
    """
    puede_asignar_superadmin = request.user.is_superuser

    if request.method == 'POST':
        post_data    = request.POST.copy()
        is_active    = request.POST.get('is_active')    == 'on'
        is_superuser = (request.POST.get('is_superuser') == 'on') if puede_asignar_superadmin else False

        # Defensa en profundidad: aunque manipulen el POST, un admin no puede escalar privilegios.
        if not puede_asignar_superadmin:
            post_data['is_superuser'] = ''

        form = RegistroForm(post_data, request.FILES)

        if form.is_valid():
            try:
                usuario              = form.save(commit=False)
                # En este sistema solo existen administradores y superadministradores.
                # Por defecto todos los usuarios del panel deben tener acceso (is_staff=True).
                usuario.is_staff     = True
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
                    f'✅ Usuario {usuario.username} creado correctamente.',
                    extra_tags='level-success field-general'
                )
                crear_notificacion(
                    categoria='movimiento',
                    estilo='success',
                    titulo='Usuario creado',
                    mensaje=f'Se creo el usuario {usuario.username}.',
                )
                return redirect('usuarios:lista_usuarios')

            except Exception as e:
                messages.error(
                    request,
                    f'❌ Error al crear usuario: {str(e)}',
                    extra_tags='level-error field-general'
                )
        else:
            # Mostrar errores reales del form (incluye password1/password2)
            for msg in build_form_messages(form):
                messages.error(request, msg['text'], extra_tags=msg['tags'])

            messages.warning(
                request,
                '⚠️ Revisa los campos resaltados y corrige los errores.',
                extra_tags='level-warning field-general'
            )

    else:
        form         = RegistroForm()
        is_active    = True
        is_staff     = True
        is_superuser = False

    context = {
        'form':          form,
        'titulo':        'Crear Nuevo Usuario',
        'boton_texto':   'Crear Usuario',
        'is_active':     is_active if request.method == 'POST' else True,
        'is_staff':      is_staff  if request.method == 'POST' else True,
        'is_superuser':  is_superuser if request.method == 'POST' else False,
        'puede_asignar_superadmin': puede_asignar_superadmin,
    }
    return render(request, 'usuarios/crear_usuario.html', context)


@login_required
@panel_login_required
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
        estado_anterior_activo = usuario.is_active

        # Nota: Validacion de confirmacion de cambio de documento desactivada a pedido.
        # if documento_original != documento_nuevo:
        #     confirmar = request.POST.get('confirmar_cambio_documento', '')
        #     if confirmar != 'CONFIRMAR':
        #         messages.error(
        #             request,
        #             '⚠️ Para cambiar el documento debes marcar la casilla de confirmación y escribir "CONFIRMAR" en el campo.',
        #             extra_tags='level-error field-documento'
        #         )
        #         form = EditarPerfilForm(request.POST, request.FILES, instance=usuario, editing_user=request.user)
        #         return render(request, 'usuarios/editar_usuario.html', {
        #             'form': form, 'usuario': usuario,
        #             'es_auto_edicion': True,
        #             'titulo': 'Editar Mi Perfil',
        #             'boton_texto': 'Guardar Cambios',
        #             'documento_original': documento_original,
        #         })

        form = EditarPerfilForm(
            request.POST,
            request.FILES,
            instance=usuario,
            editing_user=request.user
        )

        if form.is_valid():
            try:
                usuario_actualizado = form.save()

                # Misma logica de activacion/desactivacion que en vistas de admin.
                if estado_anterior_activo != usuario_actualizado.is_active and usuario_actualizado.email:
                    if not usuario_actualizado.is_active:
                        subject = 'Cuenta desactivada - Panel Administrativo Artes y Estilos'
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
                        try:
                            context = {
                                'nombre': usuario_actualizado.get_full_name() or usuario_actualizado.username,
                                'email': usuario_actualizado.email,
                            }
                            body_text = render_to_string('usuarios/email_cuenta_desactivada.txt', context)
                            body_html = render_to_string('usuarios/email_cuenta_desactivada.html', context)
                            email = EmailMultiAlternatives(subject=subject, body=body_text, from_email=from_email, to=[usuario_actualizado.email])
                            email.attach_alternative(body_html, 'text/html')
                            email.send(fail_silently=True)
                        except Exception:
                            pass
                    else:
                        subject = 'Cuenta activada - Panel Administrativo Artes y Estilos'
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
                        try:
                            context = {
                                'nombre': usuario_actualizado.get_full_name() or usuario_actualizado.username,
                                'email': usuario_actualizado.email,
                            }
                            body_text = render_to_string('usuarios/email_cuenta_activada.txt', context)
                            body_html = render_to_string('usuarios/email_cuenta_activada.html', context)
                            email = EmailMultiAlternatives(subject=subject, body=body_text, from_email=from_email, to=[usuario_actualizado.email])
                            email.attach_alternative(body_html, 'text/html')
                            email.send(fail_silently=True)
                        except Exception:
                            pass

                messages.success(
                    request,
                    '✅ Tu perfil ha sido actualizado correctamente.',
                    extra_tags='level-success field-general'
                )

                crear_notificacion(
                    categoria='movimiento',
                    estilo='info',
                    titulo='Perfil actualizado',
                    mensaje=f'Se actualizo el perfil de {usuario_actualizado.username}.',
                )

                if estado_anterior_activo != usuario_actualizado.is_active:
                    crear_notificacion(
                        categoria='cuenta',
                        estilo='success' if usuario_actualizado.is_active else 'error',
                        titulo='Cuenta activada' if usuario_actualizado.is_active else 'Cuenta desactivada',
                        mensaje=f'La cuenta de {usuario_actualizado.username} fue {"activada" if usuario_actualizado.is_active else "desactivada"}.',
                    )

                # Si se desactiva su propia cuenta, se cierra sesion de inmediato.
                if not usuario_actualizado.is_active:
                    auth_logout(request)
                    messages.warning(
                        request,
                        'Tu cuenta fue desactivada. No puedes ingresar hasta que un superadministrador la reactive.',
                        extra_tags='level-warning field-inactive'
                    )
                    return redirect('usuarios:panel_inactivo')

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

    if not usuario.is_staff:
        messages.error(request,
            '⛔ Solo puedes desactivar administradores desde esta sección.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()

        crear_notificacion(
            categoria='cuenta',
            estilo='error',
            titulo='Cuenta desactivada',
            mensaje=f'La cuenta de {usuario.username} fue desactivada.',
        )

        if usuario.email:
            subject = 'Cuenta desactivada - Panel Administrativo Artes y Estilos'
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
            try:
                context = {
                    'nombre': usuario.get_full_name() or usuario.username,
                    'email': usuario.email,
                }
                body_text = render_to_string('usuarios/email_cuenta_desactivada.txt', context)
                body_html = render_to_string('usuarios/email_cuenta_desactivada.html', context)
                email = EmailMultiAlternatives(subject=subject, body=body_text, from_email=from_email, to=[usuario.email])
                email.attach_alternative(body_html, 'text/html')
                email.send(fail_silently=True)
            except Exception:
                pass

        messages.success(request,
            f'✅ Usuario {usuario.username} desactivado correctamente.',
            extra_tags='level-success field-general')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/desactivar_usuario.html', {'usuario': usuario})


@login_required
@panel_login_required
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

    if not usuario.is_staff:
        messages.error(request,
            '⛔ Solo puedes activar administradores desde esta sección.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        usuario.is_active = True
        usuario.save()

        crear_notificacion(
            categoria='cuenta',
            estilo='success',
            titulo='Cuenta activada',
            mensaje=f'La cuenta de {usuario.username} fue activada.',
        )

        if usuario.email:
            subject = 'Cuenta activada - Panel Administrativo Artes y Estilos'
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
            try:
                context = {
                    'nombre': usuario.get_full_name() or usuario.username,
                    'email': usuario.email,
                }
                body_text = render_to_string('usuarios/email_cuenta_activada.txt', context)
                body_html = render_to_string('usuarios/email_cuenta_activada.html', context)
                email = EmailMultiAlternatives(subject=subject, body=body_text, from_email=from_email, to=[usuario.email])
                email.attach_alternative(body_html, 'text/html')
                email.send(fail_silently=True)
            except Exception:
                pass

        messages.success(request,
            f'✅ Usuario {usuario.username} activado correctamente.',
            extra_tags='level-success field-general')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/activar_usuario.html', {'usuario': usuario})


@superadmin_required
def convertir_superadmin_view(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if usuario.id == request.user.id:
        messages.error(request,
            '⛔ No puedes modificar tu propio rol a superadmin desde esta seccion.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if usuario.is_superuser:
        messages.error(request,
            '⛔ Este usuario ya es superadministrador.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if not usuario.is_staff:
        messages.error(request,
            '⛔ Solo puedes convertir administradores a superadmin.',
            extra_tags='level-error field-general')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.save()

        if usuario.email:
            subject = 'Ahora eres SuperAdmin - Panel Administrativo Artes y Estilos'
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
            try:
                context = {
                    'nombre': usuario.get_full_name() or usuario.username,
                    'email': usuario.email,
                }
                body_text = render_to_string('usuarios/email_superadmin.txt', context)
                body_html = render_to_string('usuarios/email_superadmin.html', context)
                email = EmailMultiAlternatives(subject=subject, body=body_text, from_email=from_email, to=[usuario.email])
                email.attach_alternative(body_html, 'text/html')
                email.send(fail_silently=True)
            except Exception:
                pass

        messages.success(request,
            f'✅ Usuario {usuario.username} convertido a SuperAdmin.',
            extra_tags='level-success field-general')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/convertir_superadmin.html', {'usuario': usuario})


@login_required
@panel_login_required
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
                f'⚠️ Tu cuenta {username} ha sido eliminada permanentemente.',
                extra_tags='level-warning field-general')
            return redirect('core:landing')
        else:
            messages.error(request,
                '⛔ Debes escribir "ELIMINAR" para confirmar esta acción.',
                extra_tags='level-error field-general')

    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})