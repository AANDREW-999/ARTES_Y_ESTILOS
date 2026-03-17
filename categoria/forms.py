from django import forms
import unicodedata

from .models import Categoria


class CategoriaForm(forms.ModelForm):
	class Meta:
		model = Categoria
		fields = ['nombre', 'descripcion', 'activo']
		widgets = {
			'nombre': forms.TextInput(attrs={
				'class': 'form-control',
				'id': 'id_categoria_nombre',
				'placeholder': 'Ej. Cumpleaños',
				'maxlength': '100',
				'autocomplete': 'off',
			}),
			'descripcion': forms.Textarea(attrs={
				'class': 'form-control',
				'placeholder': 'Describe cuándo usar esta categoría (opcional)',
				'rows': 3,
				'maxlength': '300',
			}),
			'activo': forms.CheckboxInput(attrs={
				'class': 'form-check-input',
			}),
		}
		labels = {
			'nombre': 'Nombre',
			'descripcion': 'Descripción',
			'activo': 'Estado activo',
		}

	def clean_nombre(self):
		nombre = (self.cleaned_data.get('nombre') or '').strip()
		if not nombre:
			raise forms.ValidationError('El nombre es obligatorio.')

		if any(char.isdigit() for char in nombre):
			raise forms.ValidationError('El nombre no puede contener numeros.')

		for char in nombre:
			if char.isspace():
				continue

			categoria_unicode = unicodedata.category(char)
			# Letras (L*) y simbolos tipo emoji (So) permitidos.
			if categoria_unicode.startswith('L') or categoria_unicode == 'So':
				continue

			raise forms.ValidationError('Solo se permiten letras y emojis en el nombre.')
		return nombre
