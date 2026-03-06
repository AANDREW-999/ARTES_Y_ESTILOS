from django import forms
from django.urls import reverse_lazy
import re

from .models import Proveedor

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

class ProveedorForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=DEPARTAMENTOS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Proveedor
        fields = [
            'tipo_documento',
            'numero_documento',
            'nombre_proveedor',
            'direccion',
            'telefono',
            'correo_electronico',
            'departamento',
            'ciudad',
            'activo'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese número de documento',
                'maxlength': '10',
                'minlength': '6',
                'inputmode': 'numeric',
                'pattern': '[0-9]{6,10}',
                'data-verificar-url': reverse_lazy('proveedores:verificar_documento'),
                'autocomplete': 'off'
            }),
            'nombre_proveedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proveedor',
                'maxlength': '150'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección del proveedor',
                'maxlength': '200'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono',
                'maxlength': '20'
            }),
            'correo_electronico': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
                'maxlength': '254'
            }),
            'ciudad': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'tipo_documento': 'Tipo de documento',
            'numero_documento': 'Número de documento',
            'nombre_proveedor': 'Nombre del proveedor',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'correo_electronico': 'Correo electrónico',
            'departamento': 'Departamento',
            'ciudad': 'Ciudad',
            'activo': 'Activo',
        }

    def clean_departamento(self):
        departamento = self.cleaned_data.get('departamento')
        if not departamento or departamento == '':
            raise forms.ValidationError('Debe seleccionar un departamento.')
        return departamento

    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')
        departamento = self.cleaned_data.get('departamento')
        if departamento and departamento != '':
            if not ciudad or ciudad == '':
                raise forms.ValidationError('Debe seleccionar una ciudad.')
        return ciudad

    def clean_tipo_documento(self):
        tipo_documento = self.cleaned_data.get('tipo_documento')
        if not tipo_documento or tipo_documento == '':
            raise forms.ValidationError('Debe seleccionar un tipo de documento.')
        return tipo_documento

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')

        if not numero_documento or str(numero_documento).strip() == '':
            raise forms.ValidationError('El número de documento es obligatorio.')

        numero_documento = str(numero_documento).strip()
        if not numero_documento.isdigit():
            raise forms.ValidationError('El documento solo debe contener números.')

        if len(numero_documento) < 6:
            raise forms.ValidationError('El documento es demasiado corto.')

        if len(numero_documento) > 10:
            raise forms.ValidationError('El documento es demasiado largo.')

        qs = Proveedor.objects.filter(numero_documento=numero_documento)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un proveedor con este documento.')

        return numero_documento

    def clean_nombre_proveedor(self):
        nombre = self.cleaned_data.get('nombre_proveedor')

        if not nombre or str(nombre).strip() == '':
            raise forms.ValidationError('El nombre del proveedor es obligatorio.')

        nombre = str(nombre).strip()

        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$", nombre):
            raise forms.ValidationError('El nombre del proveedor solo puede contener letras.')

        return nombre.title()
