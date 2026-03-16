# forms.py
from django import forms
from datetime import date
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_emision'].input_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        self.fields['fecha_emision'].required = True
        self.fields['forma_pago'].required = True

        hoy = date.today()
        self.fields['fecha_emision'].widget.attrs.setdefault('max', hoy.isoformat())
        self.fields['forma_pago'].widget.attrs.setdefault('required', 'required')

        instance = getattr(self, 'instance', None)
        is_new_instance = not instance or not getattr(instance, 'pk', None)
        if not self.is_bound and is_new_instance:
            self.initial.setdefault('fecha_emision', hoy)

    def clean_fecha_emision(self):
        fecha = self.cleaned_data.get('fecha_emision')
        if not fecha:
            raise forms.ValidationError('La fecha de emision es obligatoria.')

        hoy = date.today()
        if fecha > hoy:
            raise forms.ValidationError('La fecha no puede ser futura.')

        if fecha < date(1900, 1, 1):
            raise forms.ValidationError('La fecha es demasiado antigua.')

        return fecha

    def clean_forma_pago(self):
        forma_pago = (self.cleaned_data.get('forma_pago') or '').strip()
        if not forma_pago:
            raise forms.ValidationError('La forma de pago es obligatoria.')
        return forma_pago


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
