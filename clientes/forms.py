"""Formularios para la app clientes."""

from django import forms
from .models import Cliente
import re


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

    # -------------------------
    # VALIDACIONES PROFESIONALES
    # -------------------------

    def clean_documento(self):
        documento = self.cleaned_data.get("documento")

        if not documento:
            raise forms.ValidationError("El documento es obligatorio.")

        if not documento.isdigit():
            raise forms.ValidationError("El documento solo debe contener números.")

        if len(documento) < 6:
            raise forms.ValidationError("El documento es demasiado corto.")

        if len(documento) > 15:
            raise forms.ValidationError("El documento es demasiado largo.")

        # Validación para evitar documentos duplicados
        qs = Cliente.objects.filter(documento=documento)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ya existe un cliente con este documento.")

        return documento

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")

        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")

        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$", nombre):
            raise forms.ValidationError("El nombre solo puede contener letras.")

        return nombre.strip().title()

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido")

        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio.")

        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$", apellido):
            raise forms.ValidationError("El apellido solo puede contener letras.")

        return apellido.strip().title()

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")

        if telefono:
            telefono = telefono.replace(" ", "")

            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono solo puede contener números.")

            if len(telefono) < 7:
                raise forms.ValidationError("Número de teléfono inválido.")

        return telefono

    def clean_correo_electronico(self):
        correo = self.cleaned_data.get("correo_electronico")

        if correo:
            correo = correo.lower().strip()

        return correo