
from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'tipo_documento',
            'nombre_proveedor',
            'direccion',
            'telefono',
            'correo_electronico',
            'ciudad',
            'activo'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'nombre_proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
