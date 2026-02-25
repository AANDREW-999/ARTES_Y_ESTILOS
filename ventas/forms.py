from django import forms
from .models import Venta


class VentaForm(forms.ModelForm):

    class Meta:
        model = Venta
        fields = [
            'tipo_venta',
            'cliente',
            #'arreglo',
            'cantidad',
            'precio',
            'forma_pago',
            'con_domicilio',
            'direccion',
            'precio_envio',
            'descripcion'
        ]

        widgets = {
            'tipo_venta': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.HiddenInput(),
            #'arreglo': forms.HiddenInput(),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
            'con_domicilio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_envio': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
