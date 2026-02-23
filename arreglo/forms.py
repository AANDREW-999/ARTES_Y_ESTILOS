from django import forms
from .models import Arreglo

class ArregloForm(forms.ModelForm):
    class Meta:
        model = Arreglo
        # Campos que coinciden con tu models.py actual
        fields = ['nombre_flor', 'tipo_producto', 'descripcion', 'precio', 'imagen']
        
        # Aquí le damos los estilos de Bootstrap
        widgets = {
            'nombre_flor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Rosas Rojas'}),
            'tipo_producto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Jarrón de Vidrio'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # Validación del precio para que no sea negativo
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio and precio <= 0:
            raise forms.ValidationError("El precio debe ser un valor mayor a 0.")
        return precio