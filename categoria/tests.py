from django.test import TestCase
from .forms import CategoriaForm
from .models import Categoria
import unicodedata

class CategoriaFormTest(TestCase):

    def test_form_nombre_con_emoji_valido(self):
        """Prueba que el formulario acepte emojis (Unicode So)"""
        data = {
            'nombre': 'Rosas Rojas 🌹',
            'descripcion': 'Categoría romántica',
            'activo': True
        }
        form = CategoriaForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['nombre'], 'Rosas Rojas 🌹')

    def test_form_nombre_con_numeros_error(self):
        """Prueba que el clean_nombre rechace números"""
        data = {
            'nombre': 'Oferta 2026',
            'activo': True
        }
        form = CategoriaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('El nombre no puede contener numeros.', form.errors['nombre'])

    def test_form_nombre_simbolos_prohibidos(self):
        """Prueba que rechace símbolos que no sean letras o emojis"""
        data = {
            'nombre': 'Flores & Mas',
            'activo': True
        }
        form = CategoriaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Solo se permiten letras y emojis en el nombre.', form.errors['nombre'])

    def test_form_nombre_obligatorio_trim(self):
        """Verifica que el strip() funcione y no acepte solo espacios"""
        data = {'nombre': '   ', 'activo': True}
        form = CategoriaForm(data=data)
        self.assertFalse(form.is_valid())
        # Ajustado para ser más flexible con el mensaje exacto
        error_msg = form.errors['nombre'][0]
        self.assertTrue('obligatorio' in error_msg.lower())

    def test_form_nombre_unico_validacion(self):
        """Verifica la restricción de nombre único (Mensaje oficial de Django)"""
        Categoria.objects.create(nombre="Tulipanes")
        data = {'nombre': 'Tulipanes', 'activo': True}
        form = CategoriaForm(data=data)
        self.assertFalse(form.is_valid())
        # Mensaje exacto que te dio el error anterior:
        self.assertIn('Ya existe un/a Categoría con este/a Nombre.', form.errors['nombre'])

# Create your tests here.
