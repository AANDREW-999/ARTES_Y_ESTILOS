"""Formularios para la app clientes."""

from django import forms
from .models import Cliente


DEPARTAMENTOS = [
    ('', 'Seleccione un departamento'),
    ('Amazonas', 'Amazonas'),
    ('Antioquia', 'Antioquia'),
    ('Arauca', 'Arauca'),
    ('Atlántico', 'Atlántico'),
    ('Bolívar', 'Bolívar'),
    ('Boyacá', 'Boyacá'),
    ('Caldas', 'Caldas'),
    ('Caquetá', 'Caquetá'),
    ('Casanare', 'Casanare'),
    ('Cauca', 'Cauca'),
    ('Cesar', 'Cesar'),
    ('Chocó', 'Chocó'),
    ('Córdoba', 'Córdoba'),
    ('Cundinamarca', 'Cundinamarca'),
    ('Guainía', 'Guainía'),
    ('Guaviare', 'Guaviare'),
    ('Huila', 'Huila'),
    ('La Guajira', 'La Guajira'),
    ('Magdalena', 'Magdalena'),
    ('Meta', 'Meta'),
    ('Nariño', 'Nariño'),
    ('Norte de Santander', 'Norte de Santander'),
    ('Putumayo', 'Putumayo'),
    ('Quindío', 'Quindío'),
    ('Risaralda', 'Risaralda'),
    ('San Andrés y Providencia', 'San Andrés y Providencia'),
    ('Santander', 'Santander'),
    ('Sucre', 'Sucre'),
    ('Tolima', 'Tolima'),
    ('Valle del Cauca', 'Valle del Cauca'),
    ('Vaupés', 'Vaupés'),
    ('Vichada', 'Vichada'),
]


class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes."""

    departamento = forms.ChoiceField(
        choices=DEPARTAMENTOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Cliente
        fields = [
            'tipo_documento',
            'documento',
            'nombre',
            'apellido',
            'telefono',
            'correo_electronico',
            'direccion',
            'ciudad',
            'departamento',
        ]

        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'correo_electronico': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
        }

        labels = {
            'documento': 'Documento',
            'tipo_documento': 'Tipo de documento',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'telefono': 'Teléfono',
            'correo_electronico': 'Correo electrónico',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'departamento': 'Departamento',
        }
