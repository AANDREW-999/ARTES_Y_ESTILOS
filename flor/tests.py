from decimal import Decimal
from django.test import TestCase
from .forms import FlorForm

class FlorFormTest(TestCase):

    def test_form_precio_formato_punto_miles(self):
        """Prueba formato 1.234.567,89 (Latino/ES)"""
        data = {
            'nombre': 'Orquídea',
            'tipo_flor': 'orquidea',
            'precio': '1.500,50',
            'cantidad': 10
        }
        form = FlorForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['precio'], Decimal('1500.50'))

    def test_form_precio_formato_coma_miles(self):
        """Prueba formato 1,500.50 (EN)"""
        data = {
            'nombre': 'Tulipán',
            'tipo_flor': 'tulipan',
            'precio': '1,500.50',
            'cantidad': 5
        }
        form = FlorForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['precio'], Decimal('1500.50'))

    def test_form_precio_invalido_letras(self):
        """Prueba que el formulario rechace texto en el precio"""
        data = {
            'nombre': 'Rosa',
            'tipo_flor': 'rosa',
            'precio': 'precio_gratis',
            'cantidad': 1
        }
        form = FlorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)
        self.assertEqual(form.errors['precio'][0], "Ingresa un precio valido.")

    def test_form_precio_cero_rechazado(self):
        """
        Prueba que no acepte precio 0. 
        Usamos '0' porque pasa el Regex pero activa la validacion 'valor <= 0'
        """
        data = {
            'nombre': 'Clavel',
            'tipo_flor': 'clavel',
            'precio': '0', 
            'cantidad': 1
        }
        form = FlorForm(data=data)
        self.assertFalse(form.is_valid())
        # Ahora sí coincidirá con el mensaje de tu clean_precio
        self.assertEqual(form.errors['precio'][0], "El precio debe ser mayor a 0.")

    def test_form_descripcion_vacia_limpieza(self):
        """Prueba que el clean_descripcion ponga el texto por defecto"""
        data = {
            'nombre': 'Lirio',
            'tipo_flor': 'lirio',
            'precio': '5000',
            'cantidad': 1,
            'descripcion': '' # Vacío
        }
        form = FlorForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['descripcion'], "Sin descripcion")
# Create your tests here.
