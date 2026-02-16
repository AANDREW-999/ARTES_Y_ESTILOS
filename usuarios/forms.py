from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class RegistroForm(UserCreationForm):
    # Campos del modelo Usuario (autenticación)
    documento = forms.CharField(
        max_length=10,
        required=True,
        help_text='Debe tener exactamente 10 dígitos',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Documento (10 dígitos)',
            'autofocus': 'autofocus',
            'pattern': '[0-9]{10}',
            'inputmode': 'numeric',
            'title': 'Solo se permiten números (10 dígitos)'
        }),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        }),
    )

    first_name = forms.CharField(
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras'
        }),
    )

    last_name = forms.CharField(
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras'
        }),
    )

    # Campos del modelo Perfil (información adicional - OPCIONALES)
    telefono = forms.CharField(
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )

    direccion = forms.CharField(
        required=False,
        label='Dirección',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección (opcional)'
        })
    )

    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Fecha de nacimiento (opcional)'
        })
    )

    foto_perfil = forms.ImageField(
        required=False,
        label='Foto de perfil',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizar widgets de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
        })

        # Personalizar widget de username
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })

        # Personalizar mensajes de ayuda
        self.fields['password1'].help_text = 'La contraseña debe tener al menos 8 caracteres.'

        # Personalizar labels
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['username'].label = 'Usuario'

    class Meta:
        model = UserModel
        fields = (
            'username', 'documento', 'first_name', 'last_name', 'email',
            'password1', 'password2'
        )

    def clean_documento(self):
        doc = self.cleaned_data['documento']
        if not doc.isdigit() or len(doc) != 10:
            raise forms.ValidationError('El documento debe tener exactamente 10 dígitos.')
        existentes = UserModel.objects.filter(documento=doc)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError('Ya existe un usuario con este documento.')
        return doc

    def clean_username(self):
        username = self.cleaned_data.get('username', '')

        # Validar longitud mínima
        if len(username) < 4:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 4 caracteres.')

        # Permitir solo letras, números, guiones y guiones bajos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError('El nombre de usuario solo puede contener letras, números, guiones (-) y guiones bajos (_).')

        # Verificar si ya existe en la base de datos
        existentes = UserModel.objects.filter(username=username)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        existentes = UserModel.objects.filter(email=email)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email

    def save(self, commit=True):
        """
        Guarda el usuario y su perfil.
        El perfil se crea automáticamente mediante señales.
        """
        # Guardar el usuario (UserCreationForm ya hashea la contraseña)
        user = super().save(commit=False)

        # Asignar campos del formulario al usuario
        user.documento = self.cleaned_data.get('documento')
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')

        if commit:
            user.save()

            # Actualizar el perfil (se crea automáticamente por la señal)
            perfil = user.perfil
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.direccion = self.cleaned_data.get('direccion', '')
            perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')

            # Foto de perfil
            foto = self.cleaned_data.get('foto_perfil')
            if foto:
                perfil.foto_perfil = foto

            perfil.save()

        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o documento'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

    def clean(self):
        cleaned = super().clean()
        usuario_o_documento = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        User = get_user_model()

        if usuario_o_documento and password:
            # Si parece documento (10 dígitos), intentamos autenticar usando el username del usuario con ese documento
            if usuario_o_documento.isdigit() and len(usuario_o_documento) == 10:
                try:
                    u = User.objects.get(documento=usuario_o_documento)
                    user = authenticate(self.request, username=u.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(self.request, username=usuario_o_documento, password=password)

            if user is None:
                raise forms.ValidationError('Credenciales inválidas, verifica tu usuario/documento y contraseña.')
            self.confirm_login_allowed(user)
            self._user = user
        return cleaned

    def get_user(self):
        return getattr(self, '_user', None)
