from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario
import re

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para inicio de sesión
    Usamos el campo username para almacenar el documento
    """
    username = forms.CharField(
        label='Documento',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su documento',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )


class RegistroForm(UserCreationForm):
    """
    Formulario para registro de nuevos usuarios
    Extiende UserCreationForm de Django
    """
    # Hacemos username opcional y oculto, lo llenamos con el documento en clean_username
    username = forms.CharField(required=False, widget=forms.HiddenInput())

    documento = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.HiddenInput(),  # oculto
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        }

    def clean_documento(self):
        """Valida que el documento no exista y tenga formato válido (exactamente 10 dígitos)."""
        documento = self.cleaned_data.get('documento', '').strip()
        if not re.fullmatch(r'\d{10}', documento):
            raise forms.ValidationError('El documento debe contener exactamente 10 números.')
        if PerfilUsuario.objects.filter(documento=documento).exists():
            raise forms.ValidationError('Este documento ya está registrado.')
        return documento

    def clean_username(self):
        """Mapea el username al documento para pasar las validaciones de UserCreationForm."""
        return self.cleaned_data.get('documento', '').strip()

    def clean_email(self):
        """Valida que el email no exista en la base de datos."""
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_first_name(self):
        """Valida nombres: solo letras y espacios, longitud razonable."""
        nombre = self.cleaned_data.get('first_name', '').strip()
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,150}', nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios (mínimo 2 caracteres).')
        return nombre

    def clean_last_name(self):
        """Valida apellidos: solo letras y espacios, longitud razonable."""
        apellido = self.cleaned_data.get('last_name', '').strip()
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,150}', apellido):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios (mínimo 2 caracteres).')
        return apellido

    def clean_telefono(self):
        """Valida teléfono opcional: admite dígitos, espacios, guiones y paréntesis."""
        tel = self.cleaned_data.get('telefono', '').strip()
        if tel and not re.fullmatch(r'[\d\-() ]{7,15}', tel):
            raise forms.ValidationError('El teléfono debe tener entre 7 y 15 caracteres válidos (dígitos, espacio, guion, paréntesis).')
        return tel

    def save(self, commit=True):
        """
        Guarda el usuario y crea su perfil con el documento
        """
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('documento', '')
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            # Asegurar perfil incluso si la señal no se disparó todavía
            from .models import PerfilUsuario
            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            perfil.documento = self.cleaned_data['documento']
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.save()

        return user


class EditarUsuarioForm(forms.ModelForm):
    """
    Formulario para editar información del usuario
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'is_staff']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Usuario Activo',
            'is_staff': 'Acceso al Panel Admin',
        }


class EditarPerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario
    """
    class Meta:
        model = PerfilUsuario
        fields = ['documento', 'telefono', 'direccion', 'foto_perfil', 'fecha_nacimiento']
        widgets = {
            'documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }