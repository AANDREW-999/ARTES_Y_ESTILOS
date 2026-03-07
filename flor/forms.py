from decimal import Decimal, InvalidOperation

from django import forms

from .models import Flor

import re

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
        return descripcion or "Sin descripcion"
