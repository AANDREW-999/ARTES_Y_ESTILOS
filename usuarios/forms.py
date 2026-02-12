from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

UserModel = get_user_model()

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
        model = UserModel
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
        existentes = UserModel.objects.filter(documento=doc)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError('Ya existe un usuario con este documento.')
        return doc

    def clean_email(self):
        email = self.cleaned_data['email']
        existentes = UserModel.objects.filter(email=email)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        cleaned = self.cleaned_data
        user.documento = cleaned.get('documento')
        user.email = cleaned.get('email')
        user.nombre = cleaned.get('nombre')
        user.apellido = cleaned.get('apellido')
        user.telefono = cleaned.get('telefono')
        user.direccion = cleaned.get('direccion')
        user.fecha_nacimiento = cleaned.get('fecha_nacimiento')
        foto = cleaned.get('foto_perfil')
        if foto is not None:
            user.foto_perfil = foto
        if not user.first_name and cleaned.get('nombre'):
            user.first_name = cleaned.get('nombre')
        if not user.last_name and cleaned.get('apellido'):
            user.last_name = cleaned.get('apellido')
        if commit:
            user.save()
            self.save_m2m()
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
