from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch

from .models import Proveedor
from .forms import ProveedorForm

User = get_user_model()

# ==============================================================================
# 🏗️ CONFIGURACIÓN BASE
# ==============================================================================
class ProveedorTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "Admin12345!"
        self.user = User.objects.create_superuser(
            username='admin_test',
            documento='10101010',
            email='admin@test.com',
            password=self.password
        )
        self.client.force_login(self.user)
        
        # Proveedor de ejemplo para pruebas de edición/eliminación
        self.proveedor = Proveedor.objects.create(
            tipo_documento='CC',
            numero_documento='12345678',
            nombre_proveedor='Proveedor De Prueba',
            direccion='Calle 123',
            telefono='3001234567',
            correo_electronico='proveedor@test.com',
            departamento='Boyacá',
            ciudad='Sogamoso'
        )

# ==============================================================================
# 📊 PRUEBAS DE MODELO
# ==============================================================================
class ProveedorModelTest(ProveedorTestBase):
    def test_str_retorna_nombre_proveedor(self):
        """Verifica que la representación del modelo sea el nombre del proveedor."""
        self.assertEqual(str(self.proveedor), 'Proveedor De Prueba')

# ==============================================================================
# 📝 PRUEBAS DE FORMULARIO
# ==============================================================================
class ProveedorFormTest(ProveedorTestBase):
    def test_form_nombre_solo_letras(self):
        """Valida que el nombre no contenga números o caracteres especiales."""
        data = {
            'tipo_documento': 'NIT',
            'numero_documento': '900123456',
            'nombre_proveedor': 'Proveedor 123', # Inválido por contener números
            'direccion': 'Carrera 10',
            'telefono': '7700000',
            'departamento': 'Antioquia',
            'ciudad': 'Medellín'
        }
        form = ProveedorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre_proveedor', form.errors)

    def test_form_documento_unico(self):
        """Valida que no se permita registrar un documento ya existente."""
        data = {
            'tipo_documento': 'CC',
            'numero_documento': '12345678', # Ya existe en el setUp
            'nombre_proveedor': 'Otro Proveedor',
            'direccion': 'Calle Falsa 123',
            'telefono': '3101112233',
            'departamento': 'Cundinamarca',
            'ciudad': 'Bogotá'
        }
        form = ProveedorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('numero_documento', form.errors)

    def test_form_longitud_documento(self):
        """Valida el rango de longitud del documento (6-10 dígitos)."""
        data_corto = {'numero_documento': '12345'} # Muy corto
        form = ProveedorForm(data=data_corto)
        self.assertIn('numero_documento', form.errors)

# ==============================================================================
# 🌐 PRUEBAS DE VISTAS
# ==============================================================================
class ProveedorViewsTest(ProveedorTestBase):
    
    def test_listar_proveedores_filtro_busqueda(self):
        """Verifica que el filtro 'q' funcione en la lista."""
        url = reverse('proveedores:listar')
        response = self.client.get(url, {'q': 'Prueba'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proveedor De Prueba')

    @patch('proveedores.views.crear_notificacion')
    def test_agregar_proveedor_exitoso(self, mock_notif):
        """Verifica la creación exitosa y la llamada a la notificación."""
        url = reverse('proveedores:agregar')
        data = {
            'tipo_documento': 'NIT',
            'numero_documento': '800900100',
            'nombre_proveedor': 'Nuevo Proveedor S A S',
            'direccion': 'Zona Industrial',
            'telefono': '3209998877',
            'correo_electronico': 'nuevo@empresa.com',
            'departamento': 'Santander',
            'ciudad': 'Bucaramanga',
            'activo': True
        }
        response = self.client.post(url, data)
        # Verifica redirección y que el objeto exista en BD
        self.assertRedirects(response, reverse('proveedores:listar'))
        self.assertTrue(Proveedor.objects.filter(numero_documento='800900100').exists())
        # Verifica que se llamó a la utilidad de notificaciones
        mock_notif.assert_called_once()

    def test_eliminar_proveedor_post(self):
        """Verifica que el borrado físico funcione mediante POST."""
        url = reverse('proveedores:eliminar', args=[self.proveedor.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('proveedores:listar'))
        self.assertFalse(Proveedor.objects.filter(pk=self.proveedor.pk).exists())

    def test_verificar_documento_ajax(self):
        """Prueba la respuesta JSON de la vista de validación de documento."""
        url = reverse('proveedores:verificar_documento')
        
        # Caso 1: Documento existe
        response = self.client.get(url, {'documento': '12345678'})
        self.assertEqual(response.json(), {'existe': True})
        
        # Caso 2: Documento no existe
        response = self.client.get(url, {'documento': '00000000'})
        self.assertEqual(response.json(), {'existe': False})

    @patch('proveedores.views.render_to_pdf')
    def test_reporte_pdf_status_200(self, mock_pdf):
        """Verifica que la vista de reporte cargue correctamente."""
        # Simulamos que render_to_pdf devuelve un objeto exitoso
        from django.http import HttpResponse
        mock_pdf.return_value = HttpResponse(status=200)
        
        url = reverse('proveedores:reporte')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

# ==============================================================================
# 🔒 PRUEBAS DE SEGURIDAD
# ==============================================================================
class ProveedorSecurityTest(TestCase):
    def test_acceso_denegado_si_no_esta_autenticado(self):
        """Verifica que las vistas redirijan al login si no hay sesión activa."""
        url = reverse('proveedores:listar')
        response = self.client.get(url)
        # Django redirige al login por el decorador @login_required
        self.assertEqual(response.status_code, 302)