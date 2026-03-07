from decimal import Decimal, InvalidOperation

from django import forms

from .models import Flor


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

        raw = str(precio or "").strip()
        if not raw:
            raise forms.ValidationError("Este campo es obligatorio.")

        # Soporta 1.000.000,00, 1000000.00 y 8.000 (miles sin decimales)
        if "," in raw:
            normalizado = raw.replace(".", "").replace(",", ".")
        elif raw.count(".") >= 1 and raw.replace(".", "").isdigit():
            normalizado = raw.replace(".", "")
        else:
            normalizado = raw

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
