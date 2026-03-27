from django import forms
import unicodedata
from core.sanitize import validar_y_sanitizar
from PIL import Image
import io

from .models import Categoria

# Extensiones permitidas para imágenes
EXTENSIONES_VALIDAS_IMAGEN = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
# Tipos MIME permitidos
TIPOS_MIME_VALIDOS = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'}


class CategoriaForm(forms.ModelForm):
	class Meta:
		model = Categoria
		fields = ['nombre', 'descripcion', 'imagen', 'activo']
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
			'imagen': forms.FileInput(attrs={
				'class': 'form-control',
				'accept': 'image/*',
			}),
			'activo': forms.CheckboxInput(attrs={
				'class': 'form-check-input',
			}),
		}
		labels = {
			'nombre': 'Nombre',
			'descripcion': 'Descripción',
			'imagen': 'Imagen',
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
	
	def clean_descripcion(self):
		"""Validar y sanitizar descripción por XSS."""
		descripcion = self.cleaned_data.get('descripcion', '')
		if descripcion:
			descripcion = validar_y_sanitizar('Descripción', descripcion)
		return descripcion

	def clean_imagen(self):
		"""Validar que el archivo sea una imagen real y no un ejecutable."""
		imagen = self.cleaned_data.get('imagen')
		
		if not imagen:
			return imagen
		
		# Validar nombre de archivo
		nombre_archivo = imagen.name.lower()
		extensiones_peligrosas = {'.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js', '.zip', '.rar'}
		
		for ext_peligrosa in extensiones_peligrosas:
			if nombre_archivo.endswith(ext_peligrosa):
				raise forms.ValidationError(f'No se permiten archivos con extensión {ext_peligrosa}.')
		
		# Validar extensión de archivo
		import os
		_, ext = os.path.splitext(nombre_archivo)
		if ext.lower() not in EXTENSIONES_VALIDAS_IMAGEN:
			raise forms.ValidationError(
				f'Tipo de archivo no permitido. Solo se aceptan: {", ".join(EXTENSIONES_VALIDAS_IMAGEN)}'
			)
		
		# Validar que sea una imagen real usando PIL
		try:
			imagen.seek(0)
			img = Image.open(imagen)
			img.verify()
		except Exception as e:
			raise forms.ValidationError(
				f'El archivo no es una imagen válida. Error: {str(e)}'
			)
		
		# Validar tamaño máximo (5MB)
		tamaño_maximo = 5 * 1024 * 1024  # 5MB
		if imagen.size > tamaño_maximo:
			raise forms.ValidationError(
				f'El archivo es demasiado grande. Máximo 5MB, tu archivo tiene {imagen.size / 1024 / 1024:.2f}MB.'
			)
		
		return imagen
