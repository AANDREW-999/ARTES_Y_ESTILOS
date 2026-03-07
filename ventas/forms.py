from django import forms
import re
from decimal import Decimal, InvalidOperation
from .models import Venta


class VentaForm(forms.ModelForm):
    mano_obra = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'manoObra',
                'inputmode': 'decimal',
                'placeholder': '0,00',
                'autocomplete': 'off',
            }
        ),
    )

    class Meta:
        model  = Venta
        fields = [
            'tipo_venta',
            'cliente',
            'fecha',
            'forma_pago',
            'mano_obra',
            'con_domicilio',
            'direccion',
            'nombre_domiciliario',
            'telefono_domiciliario',
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
            'con_domicilio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'direccion':  forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_domiciliario': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del domiciliario'
            }),
            'telefono_domiciliario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3001234567',
                'inputmode': 'numeric',
                'maxlength': '20',
                'pattern': r'\+?\d{7,15}',
            }),
            'precio_envio': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'step': '0.01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3
            }),
        }

    def clean_mano_obra(self):
        raw = (self.cleaned_data.get('mano_obra') or '').strip()
        if not raw:
            return Decimal('0')

        normalizado = raw.replace('.', '').replace(',', '.')
        try:
            val = Decimal(normalizado)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError('Ingresa un valor válido para mano de obra.')

        if val < 0:
            raise forms.ValidationError('La mano de obra no puede ser negativa.')
        return val

    def clean_precio_envio(self):
        val = self.cleaned_data.get('precio_envio')
        if val is not None and val < 0:
            raise forms.ValidationError('El precio de envío no puede ser negativo.')
        return val

    def clean(self):
        cleaned_data = super().clean()

        con_domicilio = cleaned_data.get('con_domicilio')
        direccion = (cleaned_data.get('direccion') or '').strip()
        nombre_domiciliario = (cleaned_data.get('nombre_domiciliario') or '').strip()
        telefono_domiciliario = (cleaned_data.get('telefono_domiciliario') or '').strip()
        precio_envio = cleaned_data.get('precio_envio')

        if con_domicilio:
            if not direccion:
                self.add_error('direccion', 'La dirección es obligatoria cuando la venta es con domicilio.')

            if not nombre_domiciliario:
                self.add_error('nombre_domiciliario', 'El nombre del domiciliario es obligatorio.')

            if not telefono_domiciliario:
                self.add_error('telefono_domiciliario', 'El teléfono del domiciliario es obligatorio.')
            else:
                telefono_limpio = telefono_domiciliario.replace(' ', '').replace('-', '')
                if not re.fullmatch(r'\+?\d{7,15}', telefono_limpio):
                    self.add_error('telefono_domiciliario', 'Ingresa un teléfono válido (solo números, 7 a 15 dígitos).')
                else:
                    cleaned_data['telefono_domiciliario'] = telefono_limpio

            if precio_envio is None:
                self.add_error('precio_envio', 'El costo de envío es obligatorio cuando hay domicilio.')
        else:
            cleaned_data['direccion'] = ''
            cleaned_data['nombre_domiciliario'] = ''
            cleaned_data['telefono_domiciliario'] = ''
            cleaned_data['precio_envio'] = 0

        return cleaned_data