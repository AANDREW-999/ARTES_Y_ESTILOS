"""Formularios para la app clientes."""

from django import forms
from .models import Cliente
import re


class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes."""

    # Se renderiza como <select> pero se guarda como texto (CharField).
    # Las opciones se cargan dinámicamente desde la API con JS.
    departamento = forms.CharField(
        required=True,
        widget=forms.Select(attrs={'class': 'form-select js-departamento'})
    )

    ciudad = forms.CharField(
        required=True,
        widget=forms.Select(attrs={'class': 'form-select js-ciudad', 'disabled': 'disabled'})
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
                'placeholder': 'Ingrese número de documento',
                'maxlength': '10',
                'inputmode': 'numeric',
                'pattern': '[0-9]{6,10}'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese nombre completo'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese apellido completo'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese teléfono'
            }),
            'correo_electronico': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese dirección completa'
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

    def clean_tipo_documento(self):
        tipo_documento = self.cleaned_data.get("tipo_documento")

        if not tipo_documento or tipo_documento == '':
            raise forms.ValidationError("Debe seleccionar un tipo de documento.")

        return tipo_documento

    def clean_documento(self):
        documento = self.cleaned_data.get("documento")

        if not documento:
            raise forms.ValidationError("El documento es obligatorio.")

        if not documento.isdigit():
            raise forms.ValidationError("El documento solo debe contener números.")

        if len(documento) < 6:
            raise forms.ValidationError("El documento es demasiado corto.")

        if len(documento) > 10:
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

    # ========================================
    # NUEVAS VALIDACIONES DE DEPARTAMENTO Y CIUDAD
    # ========================================

    def clean_departamento(self):
        departamento = self.cleaned_data.get("departamento")

        if not departamento or departamento == '':
            raise forms.ValidationError("Debe seleccionar un departamento.")

        return departamento

    def clean_ciudad(self):
        ciudad = self.cleaned_data.get("ciudad")
        departamento = self.cleaned_data.get("departamento")

        # Solo validar ciudad si hay departamento seleccionado
        if departamento and departamento != '':
            if not ciudad or ciudad == '':
                raise forms.ValidationError("Debe seleccionar una ciudad.")

        return ciudad