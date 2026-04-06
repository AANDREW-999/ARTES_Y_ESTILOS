# forms.py
from django import forms
from datetime import date
from decimal import Decimal, InvalidOperation
from .models import Compra, DetalleCompra
from core.sanitize import validar_y_sanitizar

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
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'maxlength': '500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_emision'].input_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        self.fields['fecha_emision'].required = True
        self.fields['fecha_emision'].disabled = True
        self.fields['forma_pago'].required = True

        hoy = date.today()
        self.fields['fecha_emision'].widget.attrs.setdefault('max', hoy.isoformat())
        self.fields['fecha_emision'].widget.attrs['readonly'] = 'readonly'
        self.fields['forma_pago'].widget.attrs.setdefault('required', 'required')

        instance = getattr(self, 'instance', None)
        is_new_instance = not instance or not getattr(instance, 'pk', None)
        if is_new_instance:
            self.initial['fecha_emision'] = hoy

    def clean_fecha_emision(self):
        instance = getattr(self, 'instance', None)
        if instance and getattr(instance, 'pk', None):
            return instance.fecha_emision

        # En compras nuevas, la fecha de emisión siempre es la fecha actual.
        return date.today()

    def clean_forma_pago(self):
        forma_pago = (self.cleaned_data.get('forma_pago') or '').strip()
        if not forma_pago:
            raise forms.ValidationError('La forma de pago es obligatoria.')
        return forma_pago
    
    def clean_descripcion(self):
        """Validar y sanitizar descripción por XSS."""
        descripcion = self.cleaned_data.get('descripcion', '')
        if descripcion:
            descripcion = validar_y_sanitizar('Descripción', descripcion)
        return descripcion


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
