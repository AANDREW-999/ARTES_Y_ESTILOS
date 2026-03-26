from decimal import Decimal, InvalidOperation
from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    # Definimos precio como CharField para que acepte comas y puntos 
    # antes de procesarlos en clean_precio
    precio = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control js-money-input", 
            "inputmode": "decimal", 
            "autocomplete": "off"
        }),
        label="Precio"
    )

    class Meta:
        model = Producto
        fields = ["nombre", "tipo_producto", "descripcion", "precio", "cantidad", "imagen"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_producto": forms.Select(attrs={"class": "form-select"}),
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
        
        # Si ya es Decimal (poco probable por ser CharField, pero preventivo)
        if isinstance(precio, Decimal):
            if precio <= 0:
                raise forms.ValidationError("El precio debe ser mayor a 0.")
            return precio

        raw = str(precio or "").strip()
        if not raw:
            raise forms.ValidationError("Este campo es obligatorio.")

        # Lógica de normalización: Soporta 1.000.000,00, 1000000.00 y 8.000
        if "," in raw:
            # Caso latino: 1.500,50 -> 1500.50
            normalizado = raw.replace(".", "").replace(",", ".")
        elif raw.count(".") >= 1:
            # Caso miles sin decimales: 10.000 -> 10000
            # Solo quitamos puntos si no parece un decimal simple (como 10.50)
            parts = raw.split(".")
            if len(parts[-1]) != 2: # Si el último bloque no tiene 2 dígitos, asumimos punto de mil
                normalizado = raw.replace(".", "")
            else:
                normalizado = raw
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