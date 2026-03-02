from django import forms
from django.core.validators import MinValueValidator
from .models import Venta, IVA_CHOICES


class VentaForm(forms.ModelForm):

    class Meta:
        model  = Venta
        fields = [
            'tipo_venta',
            'cliente',
            'fecha',
            'forma_pago',
            'mano_obra',
            'iva_pct',
            'con_domicilio',
            'direccion',
            'precio_envio',
            'descripcion',
        ]

        widgets = {
            'tipo_venta': forms.Select(attrs={'class': 'form-select'}),
            'cliente':    forms.Select(attrs={'class': 'form-select'}),
            'fecha':      forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
            'mano_obra':  forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'step': '0.01'
            }),
            'iva_pct':    forms.Select(attrs={'class': 'form-select'}),
            'con_domicilio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'direccion':  forms.TextInput(attrs={'class': 'form-control'}),
            'precio_envio': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'step': '0.01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3
            }),
        }

    def clean_mano_obra(self):
        val = self.cleaned_data.get('mano_obra')
        if val is not None and val < 0:
            raise forms.ValidationError('La mano de obra no puede ser negativa.')
        return val

    def clean_precio_envio(self):
        val = self.cleaned_data.get('precio_envio')
        if val is not None and val < 0:
            raise forms.ValidationError('El precio de envío no puede ser negativo.')
        return val