from django import forms
from django.urls import reverse_lazy
import re

from .models import Proveedor
from core.sanitize import validar_y_sanitizar

class ProveedorForm(forms.ModelForm):
    # Se renderiza como <select> pero se guarda como texto (CharField).
    # Las opciones se cargan dinámicamente desde la API con JS.
    departamento = forms.CharField(
        required=True,
        widget=forms.Select(attrs={'class': 'form-select js-departamento'})
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
            'ciudad': forms.Select(attrs={'class': 'form-select js-ciudad', 'disabled': 'disabled'}),
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

        # Sanitizar contra XSS
        nombre = validar_y_sanitizar('Nombre del proveedor', nombre)
        return nombre.title()
    
    def clean_telefono(self):
        """Validar teléfono: entre 7 y 15 dígitos."""
        telefono = self.cleaned_data.get('telefono')
        
        if telefono:
            # Remover espacios y guiones
            telefono_limpio = telefono.replace(" ", "").replace("-", "")
            
            # Validar formato
            if not re.match(r"^\+?\d{7,15}$", telefono_limpio):
                raise forms.ValidationError('El teléfono debe tener entre 7 y 15 dígitos. Ejemplo: +57 3001234567')
            
            return telefono_limpio
        
        return telefono
    
    def clean_direccion(self):
        """Validar dirección: solo alfanuméricos y símbolos comunes."""
        direccion = self.cleaned_data.get('direccion')
        
        if direccion:
            # Permitir: letras, números, espacios, guiones, comas, puntos, #, etc.
            if not re.match(r"^[a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s\-#,.\(\)]{1,200}$", direccion):
                raise forms.ValidationError('La dirección contiene caracteres no permitidos.')
            
            # Sanitizar contra XSS
            direccion = validar_y_sanitizar('Dirección', direccion)
            return direccion.strip()
        
        return direccion
