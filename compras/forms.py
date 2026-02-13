# forms.py
from django import forms
from decimal import Decimal, InvalidOperation
from .models import Compra, DetalleCompra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = [
            'proveedor', 'descuento', 'forma_pago', 'medio_pago',
            'fecha_emision', 'fecha_vencimiento', 
            'departamento', 'ciudad', 'descripcion'
        ]
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def clean_descuento(self):
        """Limpiar y validar el descuento (remover formato de miles)"""
        descuento = self.cleaned_data.get('descuento')
        if descuento:
            try:
                if isinstance(descuento, str):
                    # Remover puntos (miles) y reemplazar coma por punto (decimal)
                    descuento = descuento.replace('.', '').replace(',', '.')
                    descuento = Decimal(descuento)
                else:
                    descuento = Decimal(str(descuento))
            except (InvalidOperation, ValueError):
                raise forms.ValidationError('El descuento debe ser un número válido.')
        return descuento


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['rif', 'precio', 'cantidad']
        widgets = {
            'rif': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'RIF'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control form-control-sm precio-input', 'step': '0.01', 'min': '0'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm cantidad-input', 'min': '1', 'value': '1'}),
        }
