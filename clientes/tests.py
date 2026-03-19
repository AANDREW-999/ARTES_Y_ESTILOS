# tests.py
from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import OperationalError, ProgrammingError, models
from django.http import JsonResponse
from unittest.mock import patch, MagicMock, Mock
from .models import Cliente
from django.views import generic
from .forms import ClienteForm
from .views import (
    ClienteListView, ClienteCreateView, ClienteUpdateView,
    ClienteDeleteView, ClienteDetailView, verificar_documento, DBSafeMixin
)
import json

# -----------------------------------------------------------------------------
# TESTS DEL MODELO CLIENTE
# -----------------------------------------------------------------------------
class ClienteModelTest(TestCase):
    """Pruebas unitarias para el modelo Cliente."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.cliente_data = {
            'tipo_documento': 'CC',
            'documento': '1234567890',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '3001234567',
            'correo_electronico': 'juan.perez@email.com',
            'direccion': 'Calle 123 #45-67',
            'ciudad': 'Bogotá',
            'departamento': 'Cundinamarca',
        }
        self.cliente = Cliente.objects.create(**self.cliente_data)

    def test_creacion_cliente(self):
        """Verifica que un cliente se pueda crear correctamente."""
        self.assertEqual(Cliente.objects.count(), 1)
        cliente = Cliente.objects.first()
        self.assertEqual(cliente.documento, self.cliente_data['documento'])
        self.assertEqual(str(cliente), f"Juan Pérez (1234567890)")

    def test_campos_opcionales_permiten_nulos_y_blancos(self):
        """Verifica que los campos opcionales puedan ser nulos o vacíos."""
        cliente = Cliente.objects.create(
            tipo_documento='TI',
            documento='98765432',
            nombre='Ana',
            apellido='García',
            telefono='',
            correo_electronico=None,
            direccion='',
            ciudad=None,
            departamento=''
        )
        self.assertIsNone(cliente.correo_electronico)
        self.assertEqual(cliente.telefono, '')
        self.assertIsNone(cliente.ciudad)
        self.assertEqual(cliente.departamento, '')

    def test_validator_documento_longitud_minima(self):
        """Verifica que el documento tenga al menos 6 dígitos."""
        cliente_invalido = Cliente(
            tipo_documento='CC',
            documento='12345',  # Muy corto
            nombre='Test',
            apellido='Error',
        )
        with self.assertRaises(ValidationError):
            cliente_invalido.full_clean()

    def test_validator_documento_longitud_maxima(self):
        """Verifica que el documento tenga máximo 10 dígitos."""
        cliente_invalido = Cliente(
            tipo_documento='CC',
            documento='12345678901',  # Muy largo
            nombre='Test',
            apellido='Error',
        )
        with self.assertRaises(ValidationError):
            cliente_invalido.full_clean()

    def test_validator_documento_solo_numeros(self):
        """Verifica que el documento solo contenga números."""
        cliente_invalido = Cliente(
            tipo_documento='CC',
            documento='1234A67890',
            nombre='Test',
            apellido='Error',
        )
        with self.assertRaises(ValidationError):
            cliente_invalido.full_clean()

    def test_unique_documento(self):
        """Verifica que el documento sea único."""
        cliente_duplicado = Cliente(
            tipo_documento='CC',
            documento=self.cliente_data['documento'],  # Mismo documento
            nombre='Otro',
            apellido='Cliente',
        )
        with self.assertRaises(ValidationError):
            cliente_duplicado.full_clean()

    def test_meta_ordering(self):
        """Verifica el orden por defecto (más reciente primero)."""
        Cliente.objects.all().delete()
        cliente1 = Cliente.objects.create(
            tipo_documento='CC', documento='111111', nombre='A', apellido='A'
        )
        cliente2 = Cliente.objects.create(
            tipo_documento='CC', documento='222222', nombre='B', apellido='B'
        )
        # Forzar updated_at más reciente para cliente2
        cliente2.updated_at = cliente1.updated_at + models.F('updated_at')
        cliente2.save()

        clientes = Cliente.objects.all()
        self.assertEqual(clientes.first(), cliente2)


# -----------------------------------------------------------------------------
# TESTS DEL FORMULARIO CLIENTE
# -----------------------------------------------------------------------------
class ClienteFormTest(TestCase):
    """Pruebas unitarias para el formulario ClienteForm."""

    def setUp(self):
        self.valid_data = {
            'tipo_documento': 'CC',
            'documento': '123456789',
            'nombre': 'Carlos',
            'apellido': 'Lopez',
            'telefono': '3114567890',
            'correo_electronico': 'carlos.lopez@email.com',
            'direccion': 'Carrera 1 #2-3',
            'ciudad': 'Medellín',
            'departamento': 'Antioquia',
        }

    def test_form_valido_con_datos_completos(self):
        """Verifica que el formulario sea válido con datos correctos."""
        form = ClienteForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_valido_con_datos_minimos(self):
        """Verifica que el formulario sea válido solo con datos obligatorios."""
        datos_minimos = self.valid_data.copy()
        datos_minimos.update({
            'telefono': '',
            'correo_electronico': '',
            'direccion': '',
            'ciudad': '',
            'departamento': '',  # Vaciar departamento para probar que es obligatorio
        })
        form = ClienteForm(data=datos_minimos)
        self.assertFalse(form.is_valid())
        self.assertIn('departamento', form.errors)

        # Ahora sí, con departamento (y ciudad, porque pasa a ser obligatoria)
        datos_minimos['departamento'] = 'Valle del Cauca'
        datos_minimos['ciudad'] = 'Cali'
        form = ClienteForm(data=datos_minimos)
        self.assertTrue(form.is_valid())

    def test_campos_obligatorios(self):
        """Verifica que los campos requeridos no puedan estar vacíos."""
        campos_requeridos = ['tipo_documento', 'documento', 'nombre', 'apellido', 'departamento']
        for campo in campos_requeridos:
            data_invalida = self.valid_data.copy()
            data_invalida[campo] = '' if campo != 'tipo_documento' else ''
            form = ClienteForm(data=data_invalida)
            self.assertFalse(form.is_valid())
            self.assertIn(campo, form.errors)

    def test_validacion_documento_solo_numeros(self):
        """Valida que el documento solo contenga números."""
        self.valid_data['documento'] = '12345A789'
        form = ClienteForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('documento', form.errors)
        self.assertIn('solo debe contener números', str(form.errors['documento']))

    def test_validacion_nombre_solo_letras(self):
        """Valida que el nombre solo contenga letras y espacios."""
        self.valid_data['nombre'] = 'Carlos123'
        form = ClienteForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        self.assertIn('solo puede contener letras', str(form.errors['nombre']))

    def test_validacion_apellido_solo_letras(self):
        """Valida que el apellido solo contenga letras y espacios."""
        self.valid_data['apellido'] = 'Lopez#'
        form = ClienteForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('apellido', form.errors)
        self.assertIn('solo puede contener letras', str(form.errors['apellido']))

    def test_validacion_telefono_solo_numeros(self):
        """Valida que el teléfono solo contenga números."""
        self.valid_data['telefono'] = '311-456-7890'
        form = ClienteForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)
        self.assertIn('solo puede contener números', str(form.errors['telefono']))

    def test_validacion_ciudad_requerida_con_departamento(self):
        """
        Valida que si se selecciona un departamento, la ciudad sea obligatoria.
        Lógica de clean_ciudad en el formulario.
        """
        self.valid_data['ciudad'] = ''
        form = ClienteForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ciudad', form.errors)

    def test_ciudad_opcional_sin_departamento(self):
        """
        Valida que si no hay departamento, la ciudad sea opcional.
        Nota: El departamento es obligatorio por clean_departamento.
        Así que primero forzamos que el departamento pase como None en cleaned_data para probar la lógica de clean_ciudad.
        """
        # Creamos un formulario y manipulamos cleaned_data para simular que departamento no está presente
        form = ClienteForm(data={})
        # Simulamos el estado después de la validación de campos individuales
        form.cleaned_data = {'departamento': ''}
        # Llamamos a clean_ciudad directamente
        result = form.clean_ciudad()
        # Como departamento está vacío, clean_ciudad debería devolver None o el valor existente, sin error.
        self.assertIsNone(result)  # O self.assertEqual(result, '') dependiendo de la implementación, pero devuelve None si no se setea.

    def test_documento_unico_validacion_formulario(self):
        """Verifica que no se pueda crear un cliente con un documento existente."""
        Cliente.objects.create(
            tipo_documento='CC', documento='123456789', nombre='Existente', apellido='User'
        )
        self.valid_data['documento'] = '123456789'
        form = ClienteForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('documento', form.errors)
        self.assertIn('Ya existe un cliente con este documento', str(form.errors['documento']))

    def test_documento_unico_en_edicion(self):
        """Verifica que en edición, permita el mismo documento del cliente que se edita."""
        cliente = Cliente.objects.create(
            tipo_documento='CC', documento='123456789', nombre='Existente', apellido='User'
        )
        form = ClienteForm(data=self.valid_data, instance=cliente)
        # El documento '123456789' ya existe pero es la misma instancia, debe ser válido
        self.assertTrue(form.is_valid())


# -----------------------------------------------------------------------------
# TESTS DE VISTAS (CON REQUEST FACTORY Y CLIENTE DE PRUEBA)
# -----------------------------------------------------------------------------
class ClienteViewsTest(TestCase):
    """Pruebas para las vistas CRUD de Cliente."""

    def setUp(self):
        self.factory = RequestFactory()
        self.cliente = Cliente.objects.create(
            tipo_documento='CC',
            documento='111222333',
            nombre='Maria',
            apellido='Gomez',
            telefono='3101234567',
            correo_electronico='maria@email.com',
            direccion='Calle 123 #45-67',  # Añadido para evitar None
            ciudad='Cali',
            departamento='Valle del Cauca'
        )
        self.list_url = reverse('clientes:lista_clientes')
        self.create_url = reverse('clientes:crear_cliente')
        self.detail_url = reverse('clientes:detalle_cliente', args=[self.cliente.pk])
        self.update_url = reverse('clientes:editar_cliente', args=[self.cliente.pk])
        self.delete_url = reverse('clientes:eliminar_cliente', args=[self.cliente.pk])

    # --- Pruebas para ClienteListView ---
    def test_list_view_get_queryset_sin_filtros(self):
        """Verifica que la vista de lista devuelva todos los clientes sin filtros."""
        request = self.factory.get(self.list_url)
        response = ClienteListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['clientes']), 1)

    def test_list_view_filtro_por_nombre(self):
        """Verifica el filtro de búsqueda por nombre."""
        request = self.factory.get(self.list_url, {'q': 'Maria'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 1)

        request = self.factory.get(self.list_url, {'q': 'NoExiste'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 0)

    def test_list_view_filtro_por_tipo_documento(self):
        """Verifica el filtro por tipo de documento."""
        request = self.factory.get(self.list_url, {'tipo_documento': 'CC'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 1)

        request = self.factory.get(self.list_url, {'tipo_documento': 'TI'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 0)

    def test_list_view_filtro_por_ciudad(self):
        """Verifica el filtro por ciudad."""
        request = self.factory.get(self.list_url, {'ciudad': 'Cali'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 1)

        request = self.factory.get(self.list_url, {'ciudad': 'Bogota'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 0)

    def test_list_view_filtro_por_departamento(self):
        """Verifica el filtro por departamento."""
        request = self.factory.get(self.list_url, {'departamento': 'Valle del Cauca'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 1)

        request = self.factory.get(self.list_url, {'departamento': 'Antioquia'})
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 0)

    def test_list_view_filtros_combinados(self):
        """Verifica la combinación de múltiples filtros."""
        request = self.factory.get(self.list_url, {
            'q': 'Maria',
            'tipo_documento': 'CC',
            'ciudad': 'Cali',
            'departamento': 'Valle del Cauca'
        })
        response = ClienteListView.as_view()(request)
        self.assertEqual(len(response.context_data['clientes']), 1)

    def test_list_view_context_data(self):
        """Verifica que el contexto adicional de la lista sea correcto."""
        request = self.factory.get(self.list_url)
        response = ClienteListView.as_view()(request)
        self.assertIn('total_clientes', response.context_data)
        self.assertIn('clientes_con_correo', response.context_data)
        self.assertIn('clientes_con_telefono', response.context_data)
        self.assertIn('ciudades_activas', response.context_data)
        self.assertEqual(response.context_data['total_clientes'], 1)

    def test_list_view_manejo_error_tabla_no_existe(self):
        """Verifica que la vista maneje OperationalError/ProgrammingError."""
        with patch.object(Cliente.objects, 'all', side_effect=OperationalError):
            request = self.factory.get(self.list_url)
            setattr(request, 'session', 'session')
            messages = FallbackStorage(request)
            setattr(request, '_messages', messages)

            response = ClienteListView.as_view()(request)
            self.assertEqual(response.status_code, 200)
            # Verificar que se agregó un mensaje de error
            self.assertEqual(len(messages), 1)

    # --- Pruebas para DBSafeMixin ---
    def test_db_safe_mixin_captura_error_db(self):
        """Verifica que DBSafeMixin capture OperationalError y redirija."""
        class VistaConError(DBSafeMixin, generic.View):
            def dispatch(self, request, *args, **kwargs):
                return super().dispatch(request, *args, **kwargs)

            def get(self, request):
                raise OperationalError("La tabla no existe")

        request = self.factory.get('/fake-path/')
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = VistaConError.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertEqual(response.url, reverse('clientes:lista_clientes'))
        self.assertEqual(len(messages), 1)

    # --- Pruebas para ClienteCreateView ---
    def test_create_view_get_form(self):
        """Verifica que la vista de creación cargue el formulario."""
        request = self.factory.get(self.create_url)
        response = ClienteCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], ClienteForm)

    def test_create_view_post_valido(self):
        """Verifica que se pueda crear un cliente vía POST."""
        data = {
            'tipo_documento': 'TI',
            'documento': '987654321',
            'nombre': 'Pedro',
            'apellido': 'Martinez',
            'telefono': '3155555555',
            'correo_electronico': 'pedro@email.com',
            'direccion': 'Calle 50 #20-30',
            'ciudad': 'Barranquilla',
            'departamento': 'Atlántico',
        }
        # Usamos self.client para poder usar assertRedirects si se desea
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)  # Redirige tras éxito
        self.assertRedirects(response, reverse('clientes:lista_clientes'))
        self.assertEqual(Cliente.objects.count(), 2)

    def test_create_view_post_invalido(self):
        """Verifica que con datos inválidos, el formulario muestre errores."""
        data = {
            'tipo_documento': 'CC',
            'documento': 'abc',  # Inválido
            'nombre': '',
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 200)  # Vuelve al form
        self.assertFormError(response, 'form', 'documento', 'El documento solo debe contener números.')
        self.assertFormError(response, 'form', 'nombre', 'El nombre es obligatorio.')

    # --- Pruebas para ClienteDetailView ---
    def test_detail_view_objeto_existente(self):
        """Verifica que la vista de detalle muestre el cliente correcto."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cliente'].pk, self.cliente.pk)

    def test_detail_view_objeto_no_existente(self):
        """Verifica que la vista de detalle retorne 404 si el cliente no existe."""
        response = self.client.get(reverse('clientes:detalle_cliente', args=[999]))
        self.assertEqual(response.status_code, 404)

    # --- Pruebas para ClienteUpdateView ---
    def test_update_view_get_form(self):
        """Verifica que la vista de edición cargue el formulario con los datos del cliente."""
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['form'].instance, self.cliente)

    def test_update_view_post_valido(self):
        """Verifica que se pueda actualizar un cliente vía POST."""
        data = {
            'tipo_documento': 'CC',
            'documento': self.cliente.documento,  # Mismo documento
            'nombre': 'Maria Alejandra',  # Actualizado
            'apellido': self.cliente.apellido,
            'telefono': self.cliente.telefono,
            'correo_electronico': 'maria.alejandra@email.com',  # Actualizado
            'direccion': self.cliente.direccion,
            'ciudad': self.cliente.ciudad,
            'departamento': self.cliente.departamento,
        }
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('clientes:lista_clientes'))
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nombre, 'Maria Alejandra')
        self.assertEqual(self.cliente.correo_electronico, 'maria.alejandra@email.com')

    # --- Pruebas para ClienteDeleteView ---
    def test_delete_view_get_confirmacion(self):
        """Verifica que la vista de eliminación muestre la página de confirmación."""
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cliente'], self.cliente)

    def test_delete_view_post_elimina_cliente(self):
        """Verifica que la eliminación por POST borre el cliente y redirija."""
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('clientes:lista_clientes'))
        self.assertEqual(Cliente.objects.count(), 0)

    # --- Pruebas para verificar_documento (AJAX) ---
    def test_verificar_documento_existe(self):
        """Verifica que la vista AJAX retorne {'existe': True} si el documento existe."""
        response = self.client.get(reverse('clientes:verificar_documento'), {'documento': self.cliente.documento})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['existe'])

    def test_verificar_documento_no_existe(self):
        """Verifica que la vista AJAX retorne {'existe': False} si el documento no existe."""
        response = self.client.get(reverse('clientes:verificar_documento'), {'documento': '999999999'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['existe'])

    def test_verificar_documento_sin_parametro(self):
        """Verifica que la vista AJAX retorne {'existe': False} si no se envía documento."""
        response = self.client.get(reverse('clientes:verificar_documento'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['existe'])

    def test_verificar_documento_excluye_id(self):
        """Verifica que exclude_id funcione correctamente."""
        # Crear otro cliente
        otro_cliente = Cliente.objects.create(
            tipo_documento='CC',
            documento='555666777',
            nombre='Otro',
            apellido='Cliente'
        )
        # Verificar el documento del primer cliente, excluyendo su propio ID
        response = self.client.get(
            reverse('clientes:verificar_documento'),
            {'documento': self.cliente.documento, 'exclude_id': str(self.cliente.pk)}
        )
        data = json.loads(response.content)
        self.assertFalse(data['existe'])  # Debería decir que no existe porque lo excluimos

        # Verificar el documento del primer cliente, excluyendo un ID diferente (otro_cliente)
        response = self.client.get(
            reverse('clientes:verificar_documento'),
            {'documento': self.cliente.documento, 'exclude_id': str(otro_cliente.pk)}
        )
        data = json.loads(response.content)
        self.assertTrue(data['existe'])  # Debería decir que existe


# -----------------------------------------------------------------------------
# TESTS DE URLS
# -----------------------------------------------------------------------------
class ClienteUrlsTest(TestCase):
    """Pruebas para los patrones de URL de la app clientes."""

    def test_urls_resuelven_correctamente(self):
        """Verifica que los nombres de las URLs resuelvan a las vistas correctas."""
        self.assertEqual(reverse('clientes:lista_clientes'), '/panel/clientes/')
        self.assertEqual(reverse('clientes:crear_cliente'), '/panel/clientes/crear/')
        self.assertEqual(reverse('clientes:detalle_cliente', args=[1]), '/panel/clientes/1/')
        self.assertEqual(reverse('clientes:editar_cliente', args=[1]), '/panel/clientes/1/editar/')
        self.assertEqual(reverse('clientes:eliminar_cliente', args=[1]), '/panel/clientes/1/eliminar/')
        self.assertEqual(reverse('clientes:verificar_documento'), '/panel/clientes/verificar-documento/')


# -----------------------------------------------------------------------------
# TESTS DE INTEGRACIÓN PARA JS (SIMULACIÓN DE API)
# -----------------------------------------------------------------------------
class ClienteJavaScriptIntegrationTest(TestCase):
    """
    Pruebas para la integración del frontend (JavaScript) con la API de Colombia.
    Estos tests NO ejecutan JS real, sino que simulan las llamadas a la API
    y verifican la lógica de negocio subyacente (vistas, formularios).
    """

    def test_carga_departamentos_y_ciudades_logica(self):
        """
        Verifica la lógica de negocio relacionada con departamentos/ciudades.
        Dado que el JS se encarga de llenar los selects, aseguramos que los
        valores seleccionados se guarden correctamente en el modelo.
        """
        # Simulamos que el JS ha llenado los selects con nombres de departamentos/ciudades.
        # Probamos la creación con esos nombres.
        data = {
            'tipo_documento': 'CC',
            'documento': '1010101010',
            'nombre': 'Usuario',
            'apellido': 'DePrueba',
            'departamento': 'Santander',  # El JS pondría el nombre, no el ID
            'ciudad': 'Bucaramanga',
            'telefono': '3000000000',
            'correo_electronico': 'test@test.com',
            'direccion': 'Calle Falsa 123',
        }
        response = self.client.post(reverse('clientes:crear_cliente'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        cliente_creado = Cliente.objects.get(documento='1010101010')
        self.assertEqual(cliente_creado.departamento, 'Santander')
        self.assertEqual(cliente_creado.ciudad, 'Bucaramanga')

    def test_ciudad_deshabilitada_inicialmente(self):
        """Verifica que en el formulario HTML, el select de ciudad esté deshabilitado inicialmente."""
        response = self.client.get(reverse('clientes:crear_cliente'))
        self.assertContains(response, '<select name="ciudad" id="id_ciudad" class="form-select js-ciudad" disabled>')
        self.assertNotContains(response, '<select name="ciudad" id="id_ciudad" class="form-select js-ciudad">')  # Sin disabled

    def test_departamento_original_hidden_field(self):
        """Verifica que exista el campo oculto para el valor original del departamento."""
        response = self.client.get(reverse('clientes:crear_cliente'))
        self.assertContains(response, '<input type="hidden" name="departamento_original" id="id_departamento_original" value="">')
        # Para edición
        cliente = Cliente.objects.create(
            tipo_documento='CC', documento='123', nombre='Edit', apellido='Test',
            departamento='Antioquia', ciudad='Medellín'
        )
        response = self.client.get(reverse('clientes:editar_cliente', args=[cliente.pk]))
        self.assertContains(response, f'<input type="hidden" name="departamento_original" id="id_departamento_original" value="{cliente.departamento}">')
        self.assertContains(response, f'<input type="hidden" name="ciudad_original" id="id_ciudad_original" value="{cliente.ciudad}">')