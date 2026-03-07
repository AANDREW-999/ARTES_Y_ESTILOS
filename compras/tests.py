from datetime import date

from django.test import TestCase
from django.urls import reverse

from flor.models import Flor
from producto.models import Producto
from proveedores.models import Proveedor
from usuarios.models import Usuario

from .models import Compra


class CompraStockTests(TestCase):
	def setUp(self):
		self.user = Usuario.objects.create_user(
			username="compra_tester",
			password="test12345",
			documento="1234568",
			email="compra_tester@example.com",
		)
		self.user.is_staff = True
		self.user.save(update_fields=["is_staff"])

		self.client.force_login(self.user)

		self.proveedor = Proveedor.objects.create(
			tipo_documento="NIT",
			numero_documento="900000002",
			nombre_proveedor="Proveedor Compra Test",
			direccion="Calle 1",
			telefono="3000000001",
			ciudad="Bogota",
			activo=True,
		)

		self.flor = Flor.objects.create(
			nombre="Rosa Compra Test",
			descripcion="x",
			precio=10000,
			cantidad=0,
			tipo_flor="rosa",
		)
		self.producto = Producto.objects.create(
			nombre="Globo Compra Test",
			descripcion="x",
			precio=5000,
			cantidad=0,
			tipo_producto="globos",
		)

	def _crear_compra(self, cant_flor=5, cant_producto=2):
		return self.client.post(
			reverse("compras:crear_compra"),
			{
				"proveedor": self.proveedor.id,
				"fecha_emision": date.today().isoformat(),
				"descripcion": "Compra test",
				"item_id[]": [f"F-{self.flor.id}", f"P-{self.producto.id}"],
				"precio[]": ["10000", "5000"],
				"cantidad[]": [str(cant_flor), str(cant_producto)],
			},
		)

	def test_crear_compra_aumenta_stock(self):
		response = self._crear_compra(cant_flor=10, cant_producto=4)

		self.assertEqual(response.status_code, 302)

		self.flor.refresh_from_db()
		self.producto.refresh_from_db()
		self.assertEqual(self.flor.cantidad, 10)
		self.assertEqual(self.producto.cantidad, 4)

	def test_editar_compra_ajusta_stock(self):
		self._crear_compra(cant_flor=10, cant_producto=4)
		compra = Compra.objects.latest("id")

		response = self.client.post(
			reverse("compras:editar_compra", args=[compra.id]),
			{
				"proveedor": self.proveedor.id,
				"fecha_emision": date.today().isoformat(),
				"descripcion": "Compra test editada",
				"item_id[]": [f"F-{self.flor.id}", f"P-{self.producto.id}"],
				"precio[]": ["10000", "5000"],
				"cantidad[]": ["7", "1"],
			},
		)

		self.assertEqual(response.status_code, 302)

		self.flor.refresh_from_db()
		self.producto.refresh_from_db()
		self.assertEqual(self.flor.cantidad, 7)
		self.assertEqual(self.producto.cantidad, 1)

	def test_eliminar_compra_revierte_stock(self):
		self._crear_compra(cant_flor=6, cant_producto=3)
		compra = Compra.objects.latest("id")

		response = self.client.post(reverse("compras:eliminar_compra", args=[compra.id]))

		self.assertEqual(response.status_code, 302)

		self.flor.refresh_from_db()
		self.producto.refresh_from_db()
		self.assertEqual(self.flor.cantidad, 0)
		self.assertEqual(self.producto.cantidad, 0)
