from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Producto
from categoria.models import Categoria
from decimal import Decimal

# Obtener el modelo de usuario personalizado (usuarios.Usuario)
User = get_user_model() 

class CatalogoTest(TestCase):
    def setUp(self):
        # 1. Usamos create_superuser para asegurar acceso a @panel_login_required
        self.user = User.objects.create_superuser(
            username='admin_test', 
            password='password123',
            email='admin@test.com'
        )
        self.client = Client()
        self.client.login(username='admin_test', password='password123')

        # 2. Creamos la categoría necesaria
        self.categoria = Categoria.objects.create(nombre="Ramos", activo=True)

        # 3. Producto inicial para pruebas
        # Nota: Usamos 50000 (sin punto) porque Decimal entiende el punto como separador decimal
        self.producto = Producto.objects.create(
            nombre="Girasoles Especiales",
            categoria=self.categoria,
            precio=Decimal('50000.000'),
            tamano="Grande",
            descripcion="Ramo de 12 girasoles",
            activo=True
        )

    """ --- TESTS DE URLS --- """
    def test_urls_catalogo_resuelven(self):
        # Ajustado para incluir el prefijo /panel/ que usa tu proyecto
        self.assertEqual(reverse('catalogo:gestion_productos'), '/panel/catalogo/gestion/')
        self.assertEqual(reverse('catalogo:agregar_producto'), '/panel/catalogo/agregar/')
        self.assertEqual(reverse('catalogo:detalle_producto', args=[self.producto.pk]), f'/panel/catalogo/detalle/{self.producto.pk}/')

    """ --- TESTS DE VISTAS (CRUD) --- """

    def test_lista_productos_carga_correctamente(self):
        response = self.client.get(reverse('catalogo:gestion_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Girasoles Especiales")

    def test_filtro_precio_ajusta_min_max(self):
        """Prueba la lógica donde si min > max, la vista los invierte"""
        url = reverse('catalogo:gestion_productos')
        response = self.client.get(url, {'precio_min': '100.000', 'precio_max': '50.000'})
        self.assertEqual(response.status_code, 200)
        # Verificamos el mensaje de info de tu vista
        messages = list(response.context['messages'])
        self.assertTrue(any('Se ajusto el rango' in str(m) for m in messages))

    def test_agregar_producto_post_valido(self):
        url = reverse('catalogo:agregar_producto')
        datos = {
            'nombre': 'Ramo de Rosas',
            'precio': '45.000',
            'categoria': self.categoria.id,
            'tamano': 'Mediano',
            'descripcion': 'Rosas rojas frescas',
            'activo': 'on'
        }
        # follow=True para seguir la redirección y confirmar el guardado
        response = self.client.post(url, data=datos, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Producto.objects.filter(nombre='Ramo de Rosas').exists())

    def test_editar_producto_actualiza_datos(self):
        url = reverse('catalogo:editar_producto', args=[self.producto.id])
        datos = {
            'nombre': 'Girasoles Premium',
            'precio': '60.000', # Tu vista quitará el punto -> 60000
            'categoria': self.categoria.id,
            'tamano': 'Extra Grande',
            'descripcion': 'Actualizado',
            'activo': 'on'
        }
        response = self.client.post(url, data=datos, follow=True)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Girasoles Premium')
        # Comparamos contra 60000.000 para que coincida con el valor real en BD
        self.assertEqual(self.producto.precio, Decimal('60000.000'))

    def test_eliminar_producto_borra_de_bd(self):
        url = reverse('catalogo:eliminar_producto', args=[self.producto.id])
        # follow=True asegura que lleguemos al destino final tras borrar
        response = self.client.post(url, follow=True)
        self.assertFalse(Producto.objects.filter(id=self.producto.id).exists())

    def test_detalle_producto_carga_200(self):
        url = reverse('catalogo:detalle_producto', args=[self.producto.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detalle_catalogo_producto.html')
        
    def test_agregar_producto_con_imagen_base64(self):
        url = reverse('catalogo:agregar_producto')
        
        imagen_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
        datos = {
            'nombre': 'Producto con Foto',
            'precio': '30.000',
            'categoria': self.categoria.id,
            'tamano': 'Pequeño',
            'descripcion': 'Test de imagen',
            'activo': 'on',
            'cropped_image_data': imagen_base64
        }
        
        # follow=True es vital aquí
        response = self.client.post(url, data=datos, follow=True)
        
        # 1. Verificamos que el producto se creo
        producto = Producto.objects.get(nombre='Producto con Foto')
        
        # 2. Verificamos que tiene una imagen 
        self.assertTrue(bool(producto.imagen)) 
        
        # 3. Verificamos que el nombre del archivo contiene 'producto' 
        # (usamos 'in' que es más flexible que 'startswith')
        self.assertIn('producto', producto.imagen.name.lower())

# Create your tests here.
