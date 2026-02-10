from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import Usuario

class RegistroForm(UserCreationForm):
    documento = forms.CharField(
        max_length=10,
        help_text='Debe tener exactamente 10 dígitos',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Documento (10 dígitos)'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
    )
    nombre = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fecha_nacimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    foto_perfil = forms.ImageField(required=False)

    class Meta:
        model = Usuario
        fields = (
            'username', 'documento', 'first_name', 'last_name', 'email',
            'nombre', 'apellido', 'telefono', 'direccion', 'fecha_nacimiento', 'foto_perfil',
            'password1', 'password2'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        }

    def clean_documento(self):
        doc = self.cleaned_data['documento']
        if not doc.isdigit() or len(doc) != 10:
            raise forms.ValidationError('El documento debe tener exactamente 10 dígitos.')
        if Usuario.objects.filter(documento=doc).exists():
            raise forms.ValidationError('Ya existe un usuario con este documento.')
        return doc

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email

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
