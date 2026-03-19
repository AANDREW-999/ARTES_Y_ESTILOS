from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from .models import Perfil
from .forms import LoginForm, RegistroForm, EditarPerfilForm

User = get_user_model()

# ==============================================================================
# 🏗️ CLASE BASE PARA PRUEBAS
# ==============================================================================
class UsuarioTestBase(TestCase):
    """
    Clase base que configura el entorno para las pruebas.
    Crea usuarios con diferentes niveles de permisos para testear autorizaciones.
    """
    def setUp(self):
        self.client = Client()
        self.password = "Admin12345!"
        
        # 1. Usuario Staff (Admin estándar)
        self.usuario_staff = User.objects.create_user(
            username='staff_user',
            documento='10203040',
            email='staff@test.com',
            first_name='Carlos',
            last_name='Ramírez',
            password=self.password,
            is_staff=True,
            is_active=True
        )

        # 2. SuperUsuario (Para backups y gestión sensible)
        self.superadmin = User.objects.create_superuser(
            username='superadmin_test',
            documento='12345678',
            email='superadmin@test.com',
            password=self.password
        )

# ==============================================================================
# 📊 PRUEBAS DE MODELOS
# ==============================================================================
class UsuarioModelTest(UsuarioTestBase):
    """Pruebas unitarias para los modelos Usuario y Perfil."""

    def test_creacion_perfil_automatico(self):
        """Verifica que el signal post_save cree un Perfil al crear un Usuario."""
        self.assertTrue(Perfil.objects.filter(usuario=self.usuario_staff).exists())

    def test_str_usuario_retorna_nombre_completo(self):
        """Verifica que el __str__ de Usuario retorne el nombre y apellido."""
        self.assertEqual(str(self.usuario_staff), "Carlos Ramírez")

    def test_str_perfil_formato_correcto(self):
        """Verifica que el __str__ de Perfil incluya el username."""
        perfil = self.usuario_staff.perfil
        self.assertEqual(str(perfil), f"Perfil de {self.usuario_staff.username}")

    def test_documento_debe_ser_unico(self):
        """Verifica que no se permitan documentos duplicados (IntegrityError)."""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='otro_usuario',
                documento='10203040', # Mismo documento que staff_user
                password='pass'
            )

    def test_email_debe_ser_unico(self):
        """Verifica que el correo electrónico no pueda repetirse."""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='otro_email',
                documento='99999999',
                email='staff@test.com', # Mismo email que staff_user
                password='pass'
            )

# ==============================================================================
# 📝 PRUEBAS DE FORMULARIOS
# ==============================================================================
class UsuarioFormTest(UsuarioTestBase):
    """Pruebas para validar la lógica de LoginForm, RegistroForm y EditarPerfil."""

    def test_login_form_acepta_documento(self):
        """Prueba que el LoginForm permita loguear usando el documento."""
        data = {'username': self.usuario_staff.documento, 'password': self.password}
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_login_form_acepta_username(self):
        """Prueba que el LoginForm permita loguear usando el nombre de usuario."""
        data = {'username': self.usuario_staff.username, 'password': self.password}
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_login_form_rechaza_inactivo(self):
        """Verifica que el form no valide si la cuenta está is_active=False."""
        self.usuario_staff.is_active = False
        self.usuario_staff.save()
        data = {'username': self.usuario_staff.username, 'password': self.password}
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())

    def test_registro_form_datos_correctos(self):
        """Verifica validación exitosa del formulario de registro."""
        data = {
            'username': 'nuevo_user',
            'documento': '33445566',
            'first_name': 'Ana',
            'last_name': 'Sosa',
            'email': 'ana@test.com',
            'password1': 'Ana123456!',
            'password2': 'Ana123456!',
            'telefono': '3005554433'
        }
        form = RegistroForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_registro_form_documento_corto(self):
        """Verifica que el documento sea rechazado si tiene menos de 6 dígitos."""
        data = {'documento': '12345'}
        form = RegistroForm(data=data)
        self.assertIn('documento', form.errors)

    def test_editar_perfil_form_actualiza_telefono(self):
        """Verifica que el formulario de edición actualice datos del Perfil."""
        data = {
            'first_name': 'Carlos Modificado',
            'last_name': self.usuario_staff.last_name,
            'username': self.usuario_staff.username,
            'email': self.usuario_staff.email,
            'documento': self.usuario_staff.documento,
            'telefono': '3150001122'
        }
        form = EditarPerfilForm(data=data, instance=self.usuario_staff, editing_user=self.usuario_staff)
        self.assertTrue(form.is_valid(), msg=form.errors)
        form.save()
        self.usuario_staff.refresh_from_db()
        self.assertEqual(self.usuario_staff.perfil.telefono, '3150001122')

# ==============================================================================
# 💾 PRUEBAS DEL MÓDULO DE BACKUP
# ==============================================================================
class BackupModuloTests(UsuarioTestBase):
    """Pruebas de seguridad y funcionalidad para la gestión de copias de seguridad."""

    def test_superadmin_puede_generar_backup(self):
        """Verifica que un SuperUsuario tenga permiso para descargar el backup."""
        self.client.force_login(self.superadmin)
        response = self.client.post(reverse('usuarios:generar_backup_db'))
        # Puede retornar un archivo (200) o redirigir tras éxito (302)
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            self.assertIn('attachment;', response.get('Content-Disposition', ''))
        else:
            self.assertRedirects(response, reverse('usuarios:perfil'))

    def test_admin_no_superuser_no_puede_generar_backup(self):
        """Verifica que un usuario staff (pero no superadmin) sea rechazado."""
        self.client.force_login(self.usuario_staff)
        response = self.client.post(reverse('usuarios:generar_backup_db'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_restaurar_backup_rechaza_extension_invalida(self):
        """Verifica que el sistema rechace archivos que no sean .sqlite3."""
        self.client.force_login(self.superadmin)
        invalid_file = SimpleUploadedFile('respaldo.txt', b'no-es-sqlite', content_type='text/plain')
        response = self.client.post(reverse('usuarios:restaurar_backup_db'), {'backup_file': invalid_file})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('usuarios:perfil'))

# ==============================================================================
# 🌐 PRUEBAS DE VISTAS Y ACCIONES
# ==============================================================================
class UsuarioViewsTest(UsuarioTestBase):
    """Pruebas para las vistas de gestión de usuarios."""

    @patch('usuarios.views.validar_recaptcha')
    def test_login_view_exitoso_redirige(self, mock_recaptcha):
        """Verifica que el login exitoso redirija al dashboard."""
        mock_recaptcha.return_value = True
        url = reverse('usuarios:login')
        response = self.client.post(url, {
            'username': self.usuario_staff.username,
            'password': self.password,
            'g-recaptcha-response': 'pasado'
        })
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_logout_view_limpia_sesion(self):
        """Verifica que logout redirija al landing."""
        url = reverse('usuarios:logout')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('core:landing'))

    def test_perfil_view_requiere_login(self):
        """Protección de vista: requiere estar autenticado."""
        url = reverse('usuarios:perfil')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_lista_usuarios_solo_para_staff(self):
        """Verifica que la lista de usuarios cargue correctamente para el personal."""
        self.client.login(username=self.usuario_staff.username, password=self.password)
        url = reverse('usuarios:lista_usuarios')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

def test_desactivar_usuario_view(self):
    """Prueba la acción de desactivar a otro usuario administrativo."""
    # NOTA: Agregamos is_staff=True para cumplir con la validación de la vista
    otro = User.objects.create_user(
        username='otro_staff', 
        documento='88887777', 
        password='pass',
        is_staff=True  # <--- ¡Esto es lo que faltaba!
    )
    
    self.client.force_login(self.superadmin)
    url = reverse('usuarios:desactivar_usuario', args=[otro.id])
    
    # Ejecutamos el POST
    response = self.client.post(url)
    
    # Verificamos que redirija correctamente tras el éxito
    self.assertRedirects(response, reverse('usuarios:lista_usuarios'))
    
    # Refrescamos de la BD y comprobamos
    otro.refresh_from_db()
    self.assertFalse(otro.is_active, "El usuario staff debería haber sido desactivado.")

    def test_eliminar_usuario_propio_con_confirmacion(self):
        """Verifica la eliminación por parte del propio usuario con palabra clave."""
        self.client.force_login(self.usuario_staff)
        url = reverse('usuarios:eliminar_usuario', args=[self.usuario_staff.id])
        response = self.client.post(url, {'confirmar_eliminacion': 'ELIMINAR'})
        self.assertRedirects(response, reverse('core:landing'))
        self.assertFalse(User.objects.filter(id=self.usuario_staff.id).exists())

# ==============================================================================
# 🛤️ PRUEBAS DE URLS
# ==============================================================================
class UsuarioURLTest(TestCase):
    """Verifica la resolución correcta de las rutas de la app."""

    def test_url_perfil_es_correcta(self):
        """Comprueba que la ruta del perfil resuelva a la URL esperada."""
        url = reverse('usuarios:perfil')
        self.assertEqual(url, '/panel/perfil/')