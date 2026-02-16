from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import get_user_model

from .forms import RegistroForm, LoginForm
from .utils import build_form_messages, build_login_message

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
                    f'¡Cuenta creada exitosamente! Bienvenid@ {usuario.first_name}.',
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
            if 'documento' in form.errors:
                messages.error(
                    request,
                    '⚠️ El documento ya está registrado. Si olvidaste tu contraseña, usa la opción de recuperación.',
                    extra_tags='level-error field-documento'
                )
            elif 'email' in form.errors:
                messages.error(
                    request,
                    '⚠️ El correo electrónico ya está registrado. Intenta con otro email.',
                    extra_tags='level-error field-email'
                )
            elif 'username' in form.errors:
                messages.error(
                    request,
                    '⚠️ El nombre de usuario ya está en uso. Elige otro nombre de usuario.',
                    extra_tags='level-error field-username'
                )
            else:
                messages.error(
                    request,
                    'Revisa los campos marcados en rojo y corrige los errores.',
                    extra_tags='level-error field-general'
                )

            # Agregar todos los errores del formulario
            for item in build_form_messages(form):
                messages.error(request, item['text'], extra_tags=item['tags'])
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
            messages.success(request, 'Has iniciado sesión correctamente.', extra_tags='level-success field-general')
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
            messages.success(request, 'Usuario creado correctamente.', extra_tags='level-success field-general')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.error(request, 'Revisa los campos resaltados y vuelve a intentarlo.', extra_tags='level-error field-general')
            for item in build_form_messages(form):
                messages.error(request, item['text'], extra_tags=item['tags'])
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
            messages.error(request, 'Revisa los campos resaltados y vuelve a intentarlo.', extra_tags='level-error field-general')
            for item in build_form_messages(form):
                messages.error(request, item['text'], extra_tags=item['tags'])
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
