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

# Registro
def registro(request):
    if request.method == 'POST':
        print("\n" + "="*70)
        print("🔍 DEBUG: REGISTRO DE USUARIO")
        print("="*70)
        print(f"📥 POST data: {dict(request.POST)}")
        print(f"📷 FILES data: {dict(request.FILES)}")

        form = RegistroForm(request.POST, request.FILES)

        print(f"\n✅ Formulario creado")
        print(f"🔎 ¿Es válido? {form.is_valid()}")

        if form.is_valid():
            print("\n✅ FORMULARIO VÁLIDO")
            print(f"📋 Datos limpios: {form.cleaned_data}")

            try:
                # IMPORTANTE: Primero guardamos con commit=False para modificar atributos
                usuario = form.save(commit=False)
                print(f"\n👤 Usuario creado (sin guardar): {usuario.username}")

                # Configurar permisos de acceso
                usuario.is_staff = True
                usuario.is_active = True

                # Guardar el usuario (esto dispara la señal que crea el Perfil)
                usuario.save()
                print(f"✅ Usuario guardado en BD: ID={usuario.id}")

                # Ahora actualizamos el perfil con los datos del formulario
                perfil = usuario.perfil
                print(f"✅ Perfil obtenido: ID={perfil.id}")

                perfil.telefono = form.cleaned_data.get('telefono', '')
                perfil.direccion = form.cleaned_data.get('direccion', '')
                perfil.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
                perfil.biografia = form.cleaned_data.get('biografia', '')

                print(f"📝 Datos del perfil a guardar:")
                print(f"  • Teléfono: {perfil.telefono}")
                print(f"  • Dirección: {perfil.direccion}")
                print(f"  • Fecha nac: {perfil.fecha_nacimiento}")
                print(f"  • Biografía: {perfil.biografia[:50] if perfil.biografia else '(vacío)'}")

                # Manejar la foto de perfil si existe
                foto = form.cleaned_data.get('foto_perfil')
                if foto:
                    perfil.foto_perfil = foto
                    print(f"  • Foto: {foto.name}")
                else:
                    print(f"  • Foto: (sin foto)")

                perfil.save()
                print(f"✅ Perfil guardado en BD")
                print("="*70 + "\n")

                messages.success(
                    request,
                    f'¡Cuenta creada exitosamente! Bienvenid@ {usuario.first_name} {usuario.last_name}.',
                    extra_tags='level-success field-general'
                )
                return redirect('usuarios:login')

            except Exception as e:
                print(f"\n❌ ERROR AL CREAR USUARIO: {str(e)}")
                print(f"Tipo de error: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                print("="*70 + "\n")

                messages.error(
                    request,
                    f'Error al crear la cuenta: {str(e)}',
                    extra_tags='level-error field-general'
                )
        else:
            print("\n❌ FORMULARIO INVÁLIDO")
            print(f"🔴 Errores del formulario:")
            for field, errors in form.errors.items():
                print(f"  • {field}: {errors}")
            print("="*70 + "\n")

            # Mensajes de error personalizados según el campo
            error_mostrado = False

            if 'documento' in form.errors:
                documento_value = request.POST.get('documento', '')
                messages.error(
                    request,
                    f'El documento {documento_value} ya está registrado. Si olvidaste tu contraseña, usa la opción de recuperación.',
                    extra_tags='level-error field-documento'
                )
                error_mostrado = True

            if 'email' in form.errors:
                email_value = request.POST.get('email', '')
                messages.error(
                    request,
                    f'El correo electrónico {email_value} ya está registrado. Intenta con otro email.',
                    extra_tags='level-error field-email'
                )
                error_mostrado = True

            if 'username' in form.errors:
                username_value = request.POST.get('username', '')
                messages.error(
                    request,
                    f'El nombre de usuario "{username_value}" ya está en uso. Elige otro nombre de usuario.',
                    extra_tags='level-error field-username'
                )
                error_mostrado = True

            # Si no hay errores específicos de campos únicos, mostrar mensaje general
            if not error_mostrado:
                messages.warning(
                    request,
                    'Revisa los campos marcados en rojo y corrige los errores.',
                    extra_tags='level-warning field-general'
                )

            # NO agregar mensajes adicionales del formulario para evitar duplicados
            # Los mensajes específicos ya se mostraron arriba
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


# ========================================
# 🔐 AUTENTICACIÓN
# ========================================

# Login
def login_view(request):
    """
    Vista de login para el panel administrativo.
    Solo permite acceso a usuarios con is_staff=True.
    """
    # Si el usuario ya está autenticado, redirigir al dashboard
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
            return redirect('core:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Verificar que el usuario tenga permisos de staff
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


# Logout
def logout_view(request):
    """Cierra la sesión y redirige al inicio"""
    auth_logout(request)
    messages.success(
        request,
        'Sesión cerrada correctamente. ¡Hasta pronto!',
        extra_tags='level-success field-general'
    )
    return redirect('core:index')


# ========================================
# 👤 GESTIÓN DE PERFIL PERSONAL
# ========================================

@panel_login_required
def perfil_view(request):
    """
    Vista para mostrar el perfil del usuario (solo lectura).

    URL: /panel/perfil/ver/
    """
    return render(request, 'usuarios/perfil.html')


@panel_login_required
def editar_perfil_view(request):
    """
    Vista para que el usuario edite su propio perfil.
    
    Características:
    - Solo el usuario autenticado puede editar su perfil
    - Usa EditarPerfilForm (sin contraseñas)
    - Actualiza Usuario y Perfil en una sola operación
    - Manejo correcto de archivos (foto_perfil)
    
    URL: /panel/perfil/
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
            return redirect('usuarios:editar_perfil')
        else:
            print("==== ERRORES DEL FORM ====")
            print(form.errors)
            print("==== ERRORES NO FIELD ====")
            print(form.non_field_errors())
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
    
    context = {
        'form': form,
        'usuario': usuario,
        'perfil': usuario.perfil,
    }
    return render(request, 'usuarios/editar_perfil.html', context)


# ========================================
# 👥 GESTIÓN DE USUARIOS (SOLO SUPERADMINS)
# ========================================

# ========================================
# 🔧 RECUPERACIÓN DE CONTRASEÑA
# ========================================

class RecuperarPasswordView(PasswordResetView):
    """
    Vista personalizada para recuperación de contraseña del panel.
    Envía correos en formato HTML con diseño floral elegante.

    Características:
    - Correos HTML con CSS embebido (compatible con clientes de correo)
    - Fallback a texto plano si el cliente no soporta HTML
    - Nombre de usuario personalizado en el saludo
    - Sistema seguro con tokens de Django
    - Compatible con Gmail SMTP
    """
    template_name = 'recuperar_password/solicitar_password.html'
    email_template_name = 'recuperar_password/email_recuperar_password.txt'
    html_email_template_name = 'recuperar_password/email_recuperar_password.html'
    subject_template_name = 'recuperar_password/asunto_recuperar_password.txt'
    success_url = reverse_lazy('usuarios:password_reset_done')

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sobrescribe el proceso send_mail para enviar correos HTML.

        Flujo:
        1. Renderiza el asunto (sin HTML)
        2. Renderiza versión texto plano (fallback)
        3. Renderiza versión HTML (principal)
        4. Envía ambas versiones con EmailMultiAlternatives

        Args:
            subject_template_name: Template del asunto
            email_template_name: Template de texto plano
            context: Contexto con datos del usuario y token
            from_email: Email remitente
            to_email: Email destinatario
            html_email_template_name: Template HTML (opcional)
        """
        # Renderizar asunto (strip_tags elimina cualquier HTML accidental)
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())  # Eliminar saltos de línea

        # Renderizar versión texto plano
        body_text = render_to_string(email_template_name, context)

        # Crear mensaje con texto plano como base
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[to_email]
        )

        # Si existe template HTML, renderizarlo y adjuntarlo como alternativa
        if html_email_template_name:
            body_html = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(body_html, "text/html")

        # Enviar correo
        email_message.send(fail_silently=False)

        print("\n" + "="*70)
        print("📧 CORREO DE RECUPERACIÓN ENVIADO")
        print("="*70)
        print(f"📤 Para: {to_email}")
        print(f"📋 Asunto: {subject}")
        print(f"👤 Usuario: {context.get('user', 'N/A')}")
        print(f"🔐 UID: {context.get('uid', 'N/A')}")
        print(f"🎫 Token: {context.get('token', 'N/A')[:20]}...")
        print(f"🌐 Dominio: {context.get('domain', 'N/A')}")
        print(f"📝 Formato: Texto plano + HTML")
        print("="*70 + "\n")

class RecuperarPasswordHechoView(PasswordResetDoneView):
    template_name = 'recuperar_password/solicitud_enviada.html'

class RestablecerPasswordConfirmarView(PasswordResetConfirmView):
    template_name = 'recuperar_password/confirmar_password.html'
    success_url = reverse_lazy('usuarios:password_reset_complete')

class RestablecerPasswordCompletoView(PasswordResetCompleteView):
    template_name = 'recuperar_password/password_actualizada.html'

# ========================================
# 👥 GESTIÓN DE USUARIOS (SOLO SUPERADMINS)
# ========================================

@login_required
def lista_usuarios_view(request):
    """
    Lista todos los usuarios del sistema.
    Accesible para todos los usuarios autenticados.

    Características:
    - El usuario en sesión se muestra primero en sección separada "Mi Usuario"
    - Solo puede editar/eliminar su propio perfil
    - Los demás usuarios se muestran en "Otros Usuarios" (solo lectura)
    - Validaciones en backend contra manipulación de URLs
    - Estadísticas en tiempo real

    URL: /panel/usuarios/
    """
    # Obtener el usuario actual
    usuario_actual = request.user

    # Obtener todos los usuarios excepto el actual
    otros_usuarios = User.objects.exclude(id=usuario_actual.id).select_related('perfil').order_by('-date_joined')

    # Calcular estadísticas
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    superadmins = User.objects.filter(is_superuser=True).count()
    admins = User.objects.filter(is_staff=True, is_superuser=False).count()
    usuarios_normales = User.objects.filter(is_staff=False).count()

    context = {
        'usuario_actual': usuario_actual,
        'otros_usuarios': otros_usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'superadmins': superadmins,
        'admins': admins,
        'usuarios_normales': usuarios_normales,
    }
    return render(request, 'usuarios/lista_usuarios.html', context)


@superadmin_required
def crear_usuario_view(request):
    """
    Crea un nuevo usuario en el sistema.
    Solo accesible para superadmins.
    
    Características:
    - Usa formulario personalizado para crear usuario + perfil
    - El superadmin define si es activo, staff o superuser
    - Validaciones de seguridad en backend

    URL: /panel/usuarios/crear/
    """
    if request.method == 'POST':
        # Crear una copia mutable de POST para agregar los datos
        post_data = request.POST.copy()

        # Obtener los valores de permisos (checkboxes)
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'

        # Crear el formulario base RegistroForm para manejar contraseñas
        form = RegistroForm(post_data, request.FILES)

        if form.is_valid():
            try:
                # Guardar usuario (contraseña ya hasheada por RegistroForm)
                usuario = form.save(commit=False)

                # El superadmin decide el estado inicial
                usuario.is_staff = is_staff
                usuario.is_active = is_active
                usuario.is_superuser = is_superuser

                usuario.save()

                # Actualizar perfil (la señal ya lo creó)
                perfil = usuario.perfil
                perfil.telefono = form.cleaned_data.get('telefono', '')
                perfil.direccion = form.cleaned_data.get('direccion', '')
                perfil.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
                perfil.biografia = form.cleaned_data.get('biografia', '')

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
            # Mostrar errores específicos
            error_mostrado = False

            if 'documento' in form.errors:
                documento_value = request.POST.get('documento', '')
                messages.error(
                    request,
                    f'El documento {documento_value} ya está registrado.',
                    extra_tags='level-error field-documento'
                )
                error_mostrado = True

            if 'email' in form.errors:
                email_value = request.POST.get('email', '')
                messages.error(
                    request,
                    f'El correo electrónico {email_value} ya está registrado.',
                    extra_tags='level-error field-email'
                )
                error_mostrado = True

            if 'username' in form.errors:
                username_value = request.POST.get('username', '')
                messages.error(
                    request,
                    f'El nombre de usuario "{username_value}" ya está en uso.',
                    extra_tags='level-error field-username'
                )
                error_mostrado = True

            if not error_mostrado:
                messages.warning(
                    request,
                    '⚠️ Revisa los campos resaltados y corrige los errores.',
                    extra_tags='level-warning field-general'
                )
    else:
        form = RegistroForm()
        # Establecer valores por defecto para los checkboxes
        is_active = True
        is_staff = False
        is_superuser = False

    context = {
        'form': form,
        'titulo': 'Crear Nuevo Usuario',
        'boton_texto': 'Crear Usuario',
        'is_active': is_active if request.method == 'POST' else True,
        'is_staff': is_staff if request.method == 'POST' else False,
        'is_superuser': is_superuser if request.method == 'POST' else False,
    }
    return render(request, 'usuarios/crear_usuario.html', context)


@login_required
def editar_usuario_view(request, user_id):
    """
    Edita un usuario existente.

    Restricciones de seguridad:
    - Un usuario SOLO puede editar su propio perfil (validación en backend)
    - No puede editar otros usuarios
    - Protección contra manipulación manual de URLs
    - Cambios críticos requieren confirmación (documento)
    - Redirige con mensaje de error si intenta editar otro usuario

    Validaciones:
    - Username único (excepto el usuario actual)
    - Email único (excepto el usuario actual)
    - Documento único (excepto el usuario actual)
    - Confirmación requerida para cambio de documento

    URL: /panel/usuarios/<id>/editar/
    """
    usuario = get_object_or_404(User, id=user_id)
    
    # 🔒 VALIDACIÓN CRÍTICA: Solo puede editar su propio perfil
    if usuario.id != request.user.id:
        messages.error(
            request,
            '⛔ No tienes permiso para editar este usuario. Solo puedes editar tu propio perfil.',
            extra_tags='level-error field-general'
        )
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        # Verificar si el documento cambió
        documento_original = usuario.documento
        documento_nuevo = request.POST.get('documento', '')
        documento_cambio = documento_original != documento_nuevo

        # Si el documento cambió, verificar confirmación
        if documento_cambio:
            confirmar_documento = request.POST.get('confirmar_cambio_documento', '')
            if confirmar_documento != 'CONFIRMAR':
                messages.error(
                    request,
                    '⚠️ Para cambiar el documento debes marcar la casilla de confirmación y escribir "CONFIRMAR" en el campo.',
                    extra_tags='level-error field-documento'
                )
                form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)
                context = {
                    'form': form,
                    'usuario': usuario,
                    'es_auto_edicion': True,
                    'titulo': 'Editar Mi Perfil',
                    'boton_texto': 'Guardar Cambios',
                    'documento_original': documento_original,
                }
                return render(request, 'usuarios/editar_usuario.html', context)

        # Usar EditarPerfilForm (formulario completo con todos los campos)
        form = EditarPerfilForm(
            request.POST,
            request.FILES,
            instance=usuario,
            editing_user=request.user  # Pasar usuario que está editando
        )

        if form.is_valid():
            try:
                # Guardar cambios
                form.save()

                messages.success(
                    request,
                    f'✅ Tu perfil ha sido actualizado correctamente.',
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
            # Mostrar errores específicos
            messages.warning(
                request,
                '⚠️ Revisa los campos resaltados y corrige los errores.',
                extra_tags='level-warning field-general'
            )
    else:
        form = EditarPerfilForm(
            instance=usuario,
            editing_user=request.user  # Pasar usuario que está editando
        )

    context = {
        'form': form,
        'usuario': usuario,
        'es_auto_edicion': True,  # Siempre True porque solo puede editar su propio perfil
        'titulo': 'Editar Mi Perfil',
        'boton_texto': 'Guardar Cambios',
        'documento_original': usuario.documento,
    }
    return render(request, 'usuarios/editar_usuario.html', context)


@superadmin_required
def desactivar_usuario_view(request, user_id):
    """
    Desactiva (oculta) un usuario sin eliminarlo de la base de datos.
    Solo accesible para superadmins.
    
    Arquitectura de soft-delete:
    - NO elimina el registro de la BD
    - Marca is_active=False
    - Previene que el usuario inicie sesión
    - Mantiene integridad referencial
    - Permite reactivación posterior

    Restricciones de seguridad:
    - Un superadmin NO puede desactivarse a sí mismo
    - Un superadmin NO puede desactivar a otro superadmin (debe quitarle el rol primero)
    - Requiere confirmación POST (no GET)

    URL: /panel/usuarios/<id>/desactivar/
    """
    usuario = get_object_or_404(User, id=user_id)
    
    # Validación 1: Prevenir auto-desactivación
    if usuario.id == request.user.id:
        messages.error(
            request,
            '⛔ No puedes desactivar tu propia cuenta.',
            extra_tags='level-error field-general'
        )
        return redirect('usuarios:lista_usuarios')
    
    # Validación 2: Prevenir desactivación de otro superadmin
    if usuario.is_superuser:
        messages.error(
            request,
            '⛔ No puedes desactivar a un superadministrador. '
            'Primero debes quitarle el rol de superadmin desde edición.',
            extra_tags='level-error field-general'
        )
        return redirect('usuarios:lista_usuarios')

    # Validación 3: Solo POST (no permitir desactivación por GET)
    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()

        messages.success(
            request,
            f'✅ Usuario <strong>{usuario.username}</strong> desactivado correctamente.',
            extra_tags='level-success field-general'
        )
        return redirect('usuarios:lista_usuarios')
    
    # Si es GET, mostrar confirmación
    context = {
        'usuario': usuario,
    }
    return render(request, 'usuarios/desactivar_usuario.html', context)


@login_required
def visualizar_usuario_view(request, user_id):
    """
    Muestra el detalle completo de un usuario (solo lectura).
    Accesible para todos los usuarios autenticados.

    Características:
    - Información completa del usuario y perfil
    - Todos pueden ver cualquier usuario
    - Solo botones de edición/eliminación si es el propio usuario
    - Protección contra manipulación de URLs en backend

    URL: /panel/usuarios/<id>/ver/
    """
    usuario = get_object_or_404(User.objects.select_related('perfil'), id=user_id)

    # Verificar si el usuario está viendo su propio perfil
    es_propio_perfil = (usuario.id == request.user.id)

    context = {
        'usuario': usuario,
        'perfil': usuario.perfil,
        'es_propio_perfil': es_propio_perfil,
    }
    return render(request, 'usuarios/visualizar_usuario.html', context)


@superadmin_required
def activar_usuario_view(request, user_id):
    """
    Reactiva un usuario previamente desactivado.
    Solo accesible para superadmins.

    URL: /panel/usuarios/<id>/activar/
    """
    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        usuario.is_active = True
        usuario.save()

        messages.success(
            request,
            f'✅ Usuario <strong>{usuario.username}</strong> activado correctamente.',
            extra_tags='level-success field-general'
        )
        return redirect('usuarios:lista_usuarios')

    context = {
        'usuario': usuario,
    }
    return render(request, 'usuarios/activar_usuario.html', context)


@login_required
def eliminar_usuario_view(request, user_id):
    """
    Elimina PERMANENTEMENTE un usuario de la base de datos.

    ⚠️ OPERACIÓN CRÍTICA - DESTRUCCIÓN DE DATOS ⚠️

    Restricciones de seguridad:
    - Un usuario SOLO puede eliminar su propia cuenta (validación en backend)
    - No puede eliminar otros usuarios
    - Requiere doble confirmación (escribir "ELIMINAR" + POST)
    - NO es reversible (elimina permanentemente)
    - Protección contra manipulación manual de URLs

    Recomendación: Usar desactivar_usuario_view en lugar de esta función.

    URL: /panel/usuarios/<id>/eliminar/
    """
    usuario = get_object_or_404(User, id=user_id)

    # 🔒 VALIDACIÓN CRÍTICA: Solo puede eliminar su propio perfil
    if usuario.id != request.user.id:
        messages.error(
            request,
            '⛔ No tienes permiso para eliminar este usuario. Solo puedes eliminar tu propia cuenta.',
            extra_tags='level-error field-general'
        )
        return redirect('usuarios:lista_usuarios')

    # Validación 3: Requerir confirmación explícita
    if request.method == 'POST':
        confirmacion = request.POST.get('confirmar_eliminacion')

        if confirmacion == 'ELIMINAR':
            username = usuario.username

            # Cerrar sesión antes de eliminar
            auth_logout(request)

            # Eliminar usuario
            usuario.delete()

            messages.warning(
                request,
                f'⚠️ Tu cuenta <strong>{username}</strong> ha sido eliminada permanentemente.',
                extra_tags='level-warning field-general'
            )
            return redirect('core:index')  # Redirigir al inicio público
        else:
            messages.error(
                request,
                '⛔ Debes escribir "ELIMINAR" para confirmar esta acción.',
                extra_tags='level-error field-general'
            )

    context = {
        'usuario': usuario,
    }
    return render(request, 'usuarios/eliminar_usuario.html', context)
