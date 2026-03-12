from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from flor.models import Flor
from producto.models import Producto
from usuarios.models import Usuario

from .models import Venta


class VentaStockTests(TestCase):
	def setUp(self):
		self.user = Usuario.objects.create_user(
			username="venta_tester",
			password="test12345",
			documento="1234569",
			email="venta_tester@example.com",
		)
		self.user.is_staff = True
		self.user.save(update_fields=["is_staff"])

		self.client.force_login(self.user)

		self.cliente = Cliente.objects.create(
			documento="7654322",
			tipo_documento="CC",
			nombre="Cliente Venta",
			apellido="Test",
		)

		self.flor = Flor.objects.create(
			nombre="Rosa Venta Test",
			descripcion="x",
			precio=10000,
			cantidad=10,
			tipo_flor="rosa",
		)
		self.producto = Producto.objects.create(
			nombre="Globo Venta Test",
			descripcion="x",
			precio=5000,
			cantidad=6,
			tipo_producto="globos",
		)

	def _crear_venta(self, cant_flor=3, cant_producto=2):
		return self.client.post(
			reverse("ventas:crear"),
			{
				"tipo_venta": "EI",
				"cliente": self.cliente.id,
				"fecha": date.today().isoformat(),
				"forma_pago": "efectivo",
				"mano_obra": "0",
				"precio_envio": "0",
				"descripcion": "Venta test",
				"arreglo_id[]": [f"F-{self.flor.id}", f"P-{self.producto.id}"],
				"cantidad[]": [str(cant_flor), str(cant_producto)],
				"precio[]": ["10000", "5000"],
			},
		)

	def test_crear_venta_descuenta_stock(self):
		response = self._crear_venta(cant_flor=3, cant_producto=2)
		self.assertEqual(response.status_code, 302)

		self.flor.refresh_from_db()
		self.producto.refresh_from_db()
		self.assertEqual(self.flor.cantidad, 7)
		self.assertEqual(self.producto.cantidad, 4)

	def test_crear_venta_stock_insuficiente(self):
		response = self.client.post(
			reverse("ventas:crear"),
			{
				"tipo_venta": "EI",
				"cliente": self.cliente.id,
				"fecha": date.today().isoformat(),
				"forma_pago": "efectivo",
				"mano_obra": "0",
				"precio_envio": "0",
				"descripcion": "Venta sin stock",
				"arreglo_id[]": [f"F-{self.flor.id}"],
				"cantidad[]": ["999"],
				"precio[]": ["10000"],
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(Venta.objects.count(), 0)

		self.flor.refresh_from_db()
		self.assertEqual(self.flor.cantidad, 10)

	def test_editar_venta_ajusta_stock(self):
		self._crear_venta(cant_flor=3, cant_producto=2)
		venta = Venta.objects.latest("id")

		response = self.client.post(
			reverse("ventas:editar", args=[venta.id]),
			{
				"tipo_venta": "EI",
				"cliente": self.cliente.id,
				"fecha": date.today().isoformat(),
				"forma_pago": "efectivo",
				"mano_obra": "0",
				"precio_envio": "0",
				"descripcion": "Venta editada",
				"arreglo_id[]": [f"F-{self.flor.id}", f"P-{self.producto.id}"],
				"cantidad[]": ["5", "1"],
				"precio[]": ["10000", "5000"],
			},
		)

		self.assertEqual(response.status_code, 302)

		self.flor.refresh_from_db()
		self.producto.refresh_from_db()
		self.assertEqual(self.flor.cantidad, 5)
		self.assertEqual(self.producto.cantidad, 5)

	def test_eliminar_venta_devuelve_stock(self):
		self._crear_venta(cant_flor=4, cant_producto=3)
		venta = Venta.objects.latest("id")

		response = self.client.post(reverse("ventas:eliminar", args=[venta.id]))
		self.assertEqual(response.status_code, 302)

		self.flor.refresh_from_db()
		self.producto.refresh_from_db()
		self.assertEqual(self.flor.cantidad, 10)
		self.assertEqual(self.producto.cantidad, 6)

	def test_subtotal_y_total_se_guardan_correctamente(self):
		response = self.client.post(
			reverse("ventas:crear"),
			{
				"tipo_venta": "EI",
				"cliente": self.cliente.id,
				"fecha": date.today().isoformat(),
				"forma_pago": "efectivo",
				"mano_obra": "5000",
				"con_domicilio": "on",
				"direccion": "Calle 123",
				"nombre_domiciliario": "Juan Domicilio",
				"telefono_domiciliario": "3001234567",
				"precio_envio": "2000",
				"descripcion": "Venta con adicionales",
				"arreglo_id[]": [f"F-{self.flor.id}", f"P-{self.producto.id}"],
				"cantidad[]": ["3", "2"],
				"precio[]": ["10000", "5000"],
			},
		)

		self.assertEqual(response.status_code, 302)

		venta = Venta.objects.latest("id")
		self.assertEqual(float(venta.subtotal), 40000.0)
		self.assertEqual(float(venta.total), 47000.0)


class VentaFiltroListadoTests(TestCase):
	def setUp(self):
		self.user = Usuario.objects.create_user(
			username="venta_filtro_tester",
			password="test12345",
			documento="1234570",
			email="venta_filtro@example.com",
		)
		self.user.is_staff = True
		self.user.save(update_fields=["is_staff"])

		self.client.force_login(self.user)

		self.cliente_1 = Cliente.objects.create(
			documento="8001001",
			tipo_documento="CC",
			nombre="Ana",
			apellido="Garcia",
		)
		self.cliente_2 = Cliente.objects.create(
			documento="8001002",
			tipo_documento="CC",
			nombre="Luis",
			apellido="Perez",
		)

		Venta.objects.create(
			cliente=self.cliente_1,
			tipo_venta="EI",
			fecha=date.today() - timedelta(days=10),
			forma_pago="efectivo",
			subtotal=10000,
			total=10000,
		)
		Venta.objects.create(
			cliente=self.cliente_2,
			tipo_venta="EI",
			fecha=date.today(),
			forma_pago="efectivo",
			subtotal=20000,
			total=20000,
		)

	def test_filtra_por_nombre_completo_cliente(self):
		response = self.client.get(reverse("ventas:listar_venta"), {"cliente_nombre": "Ana Garcia"})

		self.assertEqual(response.status_code, 200)
		ventas = list(response.context["ventas"])
		self.assertEqual(len(ventas), 1)
		self.assertEqual(ventas[0].cliente_id, self.cliente_1.id)

	def test_filtra_por_fecha_desde(self):
		fecha_filtro = (date.today() - timedelta(days=2)).isoformat()
		response = self.client.get(reverse("ventas:listar_venta"), {"fecha_desde": fecha_filtro})

		self.assertEqual(response.status_code, 200)
		ventas = list(response.context["ventas"])
		self.assertEqual(len(ventas), 1)
		self.assertEqual(ventas[0].cliente_id, self.cliente_2.id)

	def test_filtra_por_precio_min(self):
		response = self.client.get(reverse("ventas:listar_venta"), {"precio_min": "15000"})

		self.assertEqual(response.status_code, 200)
		ventas = list(response.context["ventas"])
		self.assertEqual(len(ventas), 1)
		self.assertEqual(ventas[0].cliente_id, self.cliente_2.id)

	def test_filtra_por_rango_precio(self):
		response = self.client.get(
			reverse("ventas:listar_venta"),
			{"precio_min": "9000", "precio_max": "12000"},
		)

		self.assertEqual(response.status_code, 200)
		ventas = list(response.context["ventas"])
		self.assertEqual(len(ventas), 1)
		self.assertEqual(ventas[0].cliente_id, self.cliente_1.id)
