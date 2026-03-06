from django import forms

from .models import Categoria


class CategoriaForm(forms.ModelForm):
	class Meta:
		model = Categoria
		fields = ['nombre', 'descripcion', 'activo']
		widgets = {
			'nombre': forms.TextInput(attrs={
				'class': 'form-control',
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
		return nombre
