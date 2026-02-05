"""Formularios para la app clientes.

Contiene ClienteForm y la lista de departamentos usada por el formulario.
No se modifica la lógica de validación ni los widgets, solo se mejora el formato.
"""

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
    """Formulario ModelForm para crear/editar Clientes.

    - departamento: ChoiceField con los 32 departamentos.
    - ciudad_id: ChoiceField vacío que se poblrá por JavaScript.
    """
    departamento = forms.ChoiceField(
        choices=DEPARTAMENTOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    ciudad_id = forms.ChoiceField(
        choices=[('', 'Seleccione ciudad')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Cliente
        fields = [
            'documento', 'tipo_documento', 'nombre', 'apellido', 'telefono',
            'correo_electronico', 'direccion', 'ciudad_id', 'departamento'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa'}),
        }
        labels = {
            'documento': 'Documento',
            'tipo_documento': 'Tipo de documento',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'telefono': 'Teléfono',
            'correo_electronico': 'Correo electrónico',
            'direccion': 'Dirección',
            'ciudad_id': 'Ciudad (ID)',
            'departamento': 'Departamento',
        }
