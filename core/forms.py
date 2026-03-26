from django import forms
import re

class ContactoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Tu nombre",
                "maxlength": "100"
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "tucorreo@ejemplo.com",
                "maxlength": "254"
            }
        ),
    )
    mensaje = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Cuentanos que necesitas",
                "maxlength": "5000"
            }
        ),
    )
    
    def clean_nombre(self):
        """Validar que el nombre solo contenga letras, espacios y caracteres básicos."""
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        
        if not nombre:
            raise forms.ValidationError('El nombre es obligatorio.')
        
        # Permitir solo letras, números, espacios y guiones
        if not re.match(r"^[a-zA-Záéíóúñ\s\-']{1,100}$", nombre):
            raise forms.ValidationError('El nombre contiene caracteres no permitidos.')
        
        return nombre
    
    def clean_mensaje(self):
        """Validar mensaje y limitar líneas."""
        mensaje = (self.cleaned_data.get('mensaje') or '').strip()
        
        if not mensaje:
            raise forms.ValidationError('El mensaje es obligatorio.')
        
        # Limitar a 50 líneas máximo
        lineas = mensaje.split('\n')
        if len(lineas) > 50:
            raise forms.ValidationError('El mensaje no puede exceder 50 líneas.')
        
        # Verificar longitud mínima
        if len(mensaje) < 10:
            raise forms.ValidationError('El mensaje debe tener al menos 10 caracteres.')
        
        return mensaje