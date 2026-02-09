# forms.py
from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = [
            'cantidad', 'precio', 'descuento', 'iva', 'total_compra',
             'descripcion', 'forma_pago', 'medio_pago',
            'fecha_emision', 'fecha_vencimiento', 'proveedor_id',
            'departamento', 'ciudad'
        ]
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
