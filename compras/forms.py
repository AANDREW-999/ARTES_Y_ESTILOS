# forms.py
from django import forms
from decimal import Decimal, InvalidOperation
from .models import Compra, DetalleCompra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = [
            'proveedor', 'forma_pago',
            'fecha_emision', 
            'descripcion'
        ]
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['tipo_item', 'flor', 'producto', 'precio', 'cantidad']
        widgets = {
            'tipo_item': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'flor': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'producto': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control form-control-sm precio-input', 'step': '0.01', 'min': '0'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm cantidad-input', 'min': '1', 'value': '1'}),
        }
