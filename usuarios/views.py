from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import RegistroForm, LoginForm
from .utils import build_login_message

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

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
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

@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')

# Logout
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Sesión cerrada correctamente. ¡Hasta pronto!', extra_tags='level-success field-general')
    return redirect('core:index')

# Recuperación de contraseña
class RecuperarPasswordView(PasswordResetView):
    """
    Vista personalizada para recuperación de contraseña.
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
            messages.success(request, 'Usuario creado correctamente.', extra_tags='level-success field-general')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.warning(request, 'Revisa los campos resaltados y vuelve a intentarlo.', extra_tags='level-warning field-general')
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
            messages.success(request, 'Usuario actualizado correctamente.', extra_tags='level-success field-general')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.warning(request, 'Revisa los campos resaltados y vuelve a intentarlo.', extra_tags='level-warning field-general')
    else:
        form = RegistroForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
def eliminar_usuario_view(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        usuario.delete()
        messages.info(request, 'Usuario eliminado.', extra_tags='level-warning field-general')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})
