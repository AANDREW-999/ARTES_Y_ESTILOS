from decimal import Decimal, InvalidOperation

from django import forms

from .models import Flor

import re
from core.sanitize import validar_y_sanitizar
from PIL import Image
import os

# Extensiones permitidas para imágenes
EXTENSIONES_VALIDAS_IMAGEN = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

class FlorForm(forms.ModelForm):
    precio = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control js-money-input",
                "inputmode": "decimal",
                "autocomplete": "off",
                "id": "id_precio",
            }
        )
    )

    class Meta:
        model = Flor
        fields = ["nombre", "tipo_flor", "descripcion", "precio", "cantidad", "imagen"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_flor": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "imagen": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "id": "image-input",
                "accept": "image/*",
            }),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if isinstance(precio, Decimal):
            return precio

        raw = str(precio or "").strip().replace(" ", "")
        if not raw:
            raise forms.ValidationError("Este campo es obligatorio.")

        # 1) 1.234.567,89  (ES)
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?", raw):
            normalizado = raw.replace(".", "").replace(",", ".")
        # 2) 1,234,567.89  (EN)
        elif re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?", raw):
            normalizado = raw.replace(",", "")
        # 3) 1234567,89 o 1234567.89 o 9000
        elif re.fullmatch(r"\d+(?:[.,]\d{1,2})?", raw):
            normalizado = raw.replace(",", ".")
        else:
            raise forms.ValidationError("Ingresa un precio valido.")

        try:
            valor = Decimal(normalizado)
        except InvalidOperation:
            raise forms.ValidationError("Ingresa un precio valido.")

        if valor <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return valor

    def clean_descripcion(self):
        descripcion = (self.cleaned_data.get("descripcion") or "").strip()
        if descripcion:
            descripcion = validar_y_sanitizar('Descripción', descripcion)
        return descripcion or "Sin descripcion"

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
