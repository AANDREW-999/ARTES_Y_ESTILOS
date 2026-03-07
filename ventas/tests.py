from datetime import date

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
