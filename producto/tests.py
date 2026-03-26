from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Producto
from .forms import ProductoForm

User = get_user_model()

class ProductoModuleTest(TestCase):
    def setUp(self):
        # 1. Configuración de usuario administrativo
        self.user = User.objects.create_superuser(username='admin_sena', password='123')
        self.client = Client()
        self.client.login(username='admin_sena', password='123')

        # 2. Productos base para las pruebas de ListView y Reportes
        self.p1 = Producto.objects.create(
            nombre="Caja de Chocolates",
            precio=Decimal("25000.00"),
            cantidad=20,
            tipo_producto="chocolates"
        )
        self.p2 = Producto.objects.create(
            nombre="Oso Gigante",
            precio=Decimal("80000.00"),
            cantidad=5,  # Bajo stock
            tipo_producto="peluches"
        )

    # ────────────────────────────────────────────────
    #  TESTS DE FORMULARIO (VALIDACIÓN DE PRECIOS)
    # ────────────────────────────────────────────────

    def test_form_precio_coma_decimal(self):
        """Prueba que '1500,50' se convierta correctamente a Decimal"""
        data = {
            'nombre': 'Vino Tinto',
            'tipo_producto': 'vinos',
            'precio': '1500,50', 
            'cantidad': 10,
            'descripcion': 'Cosecha especial'
        }
        form = ProductoForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['precio'], Decimal('1500.50'))

    def test_form_precio_punto_miles(self):
        """Prueba que '10.000' se convierta a 10000 (sin puntos)"""
        data = {
            'nombre': 'Arreglo Premium',
            'tipo_producto': 'decoraciones',
            'precio': '10.000', 
            'cantidad': 1,
            'descripcion': 'Prueba de miles'
        }
        form = ProductoForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['precio'], Decimal('10000'))

    def test_form_precio_negativo_error(self):
        """Verifica que el clean_precio bloquee valores negativos"""
        data = {
            'nombre': 'Globo', 
            'tipo_producto': 'globos',
            'precio': '-500', 
            'cantidad': 1
        }
        form = ProductoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('El precio debe ser mayor a 0.', form.errors['precio'])

    # ────────────────────────────────────────────────
    #  TESTS DE CRUD (ACCIONES EN BASE DE DATOS)
    # ────────────────────────────────────────────────

    def test_crud_crear_producto_post(self):
        """Prueba la creación real desde la vista con redirección"""
        url = reverse('producto:crear')
        data = {
            'nombre': 'Nuevo Peluche Peludo',
            'tipo_producto': 'peluches',
            'precio': '45.000', # Formato con punto de miles
            'cantidad': 12,
            'descripcion': 'Suave y grande'
        }
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('producto:lista'))
        self.assertTrue(Producto.objects.filter(nombre='Nuevo Peluche Peludo').exists())

    def test_crud_editar_producto_post(self):
        """Prueba la edición y actualización de campos"""
        url = reverse('producto:editar', args=[self.p1.id])
        data = {
            'nombre': 'Chocolates Ferrero',
            'tipo_producto': 'chocolates',
            'precio': '32500,75', # Cambio de precio con decimal
            'cantidad': 15,
            'descripcion': 'Actualizado'
        }
        response = self.client.post(url, data=data)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.nombre, 'Chocolates Ferrero')
        self.assertEqual(self.p1.precio, Decimal('32500.75'))

    def test_crud_eliminar_producto_post(self):
        """Prueba la eliminación física del registro"""
        url = reverse('producto:eliminar', args=[self.p2.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('producto:lista'))
        self.assertFalse(Producto.objects.filter(id=self.p2.id).exists())

    # ────────────────────────────────────────────────
    #  TESTS DE LÓGICA DE NEGOCIO Y REPORTES
    # ────────────────────────────────────────────────

    def test_vista_ajuste_precios_invertidos(self):
        """Prueba que la ListView corrija el rango si Min > Max"""
        url = reverse('producto:lista')
        response = self.client.get(url, {'precio_min': '50.000', 'precio_max': '10.000'})
        self.assertEqual(response.context['precio_min_filtro'], '10000')
        self.assertEqual(response.context['precio_max_filtro'], '50000')

    def test_reporte_valor_inventario_total(self):
        """Verifica que el cálculo de inventario sea exacto"""
        url = reverse('producto:reporte')
        response = self.client.get(url)
        # (25000 * 20) + (80000 * 5) = 900.000
        self.assertEqual(response.context['valor_inventario'], Decimal('900000.00'))
# Create your tests here.
