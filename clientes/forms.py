"""Formularios para la app clientes."""

from django import forms
from .models import Cliente
import re
from core.sanitize import validar_y_sanitizar


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
        
        # ===== NUEVO: Mensajes personalizados para campos requeridos =====
        error_messages = {
            'nombre': {
                'required': 'El nombre es obligatorio.',
            },
            'apellido': {
                'required': 'El apellido es obligatorio.',
            },
            'documento': {
                'required': 'El documento es obligatorio.',
            },
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
            # Este caso ahora será manejado por error_messages['documento']['required']
            # pero mantenemos la validación por si acaso
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

        # ===== CAMBIADO: No validar "requerido" aquí, dejar que error_messages lo maneje =====
        if not nombre:
            return nombre  # Django agregará el error de campo requerido automáticamente

        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$", nombre):
            raise forms.ValidationError("El nombre solo puede contener letras.")

        # Sanitizar contra XSS
        nombre = validar_y_sanitizar('Nombre', nombre)
        return nombre.strip().title()

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido")

        # ===== CAMBIADO: No validar "requerido" aquí, dejar que error_messages lo maneje =====
        if not apellido:
            return apellido  # Django agregará el error de campo requerido automáticamente

        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$", apellido):
            raise forms.ValidationError("El apellido solo puede contener letras.")

        # Sanitizar contra XSS
        apellido = validar_y_sanitizar('Apellido', apellido)
        return apellido.strip().title()

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")

        if telefono:
            # Remover espacios
            telefono_limpio = telefono.replace(" ", "").replace("-", "")
            
            # Validar que sia solo dígitos (y opcionalmente + al inicio)
            if not re.match(r"^\+?\d{7,15}$", telefono_limpio):
                raise forms.ValidationError("El teléfono debe contener entre 7 y 15 dígitos. Formato: +57 3001234567")

            return telefono_limpio

        return telefono
    
    def clean_direccion(self):
        """Validar dirección: solo alfanuméricos, espacios y símbolos comunes."""
        direccion = self.cleaned_data.get("direccion")
        
        if direccion:
            # Permitir: letras, números, espacios, guiones, comas, puntos, #, etc.
            if not re.match(r"^[a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s\-#,.\(\)]{1,200}$", direccion):
                raise forms.ValidationError("La dirección contiene caracteres no permitidos.")
            
            # Sanitizar contra XSS
            direccion = validar_y_sanitizar('Dirección', direccion)
            return direccion.strip()
        
        return direccion

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