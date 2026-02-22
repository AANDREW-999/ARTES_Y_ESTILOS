from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class EditarPerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario autenticado.

    Características:
    - Edita campos del modelo Usuario (username, first_name, last_name, email)
    - Edita campos del modelo Perfil (telefono, direccion, fecha_nacimiento, biografia, foto_perfil)
    - NO incluye contraseñas (usar sistema de cambio de contraseña de Django)
    - Validaciones para evitar duplicados de username y email
    - Manejo correcto de archivos (foto_perfil)

    Arquitectura:
    - El formulario base es ModelForm sobre Usuario
    - Los campos de Perfil se agregan como campos extra
    - El método save() actualiza ambos modelos
    """

    # Campos del modelo Usuario
    username = forms.CharField(
        required=True,
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
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

    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        }),
    )

    # Campos del modelo Perfil
    telefono = forms.CharField(
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono'
        })
    )

    direccion = forms.CharField(
        required=False,
        label='Dirección',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección'
        })
    )

    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Fecha de nacimiento'
        })
    )

    biografia = forms.CharField(
        required=False,
        label='Biografía',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Cuéntanos sobre ti',
            'rows': 4
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

    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si existe la instancia y tiene perfil, pre-cargar datos del perfil
        if self.instance and hasattr(self.instance, 'perfil'):
            perfil = self.instance.perfil
            self.fields['telefono'].initial = perfil.telefono
            self.fields['direccion'].initial = perfil.direccion
            self.fields['fecha_nacimiento'].initial = perfil.fecha_nacimiento
            self.fields['biografia'].initial = perfil.biografia
            # No pre-cargamos foto_perfil para evitar problemas con FileField

    def clean_username(self):
        """Validar que el username no esté en uso por otro usuario"""
        username = self.cleaned_data.get('username', '')

        # Validar longitud mínima
        if len(username) < 4:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 4 caracteres.')

        # Validar caracteres permitidos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError('El nombre de usuario solo puede contener letras, números, guiones (-) y guiones bajos (_).')

        # Verificar que no esté en uso (excluyendo el usuario actual)
        existentes = UserModel.objects.filter(username=username)
        if self.instance and self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')

        return username

    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        email = self.cleaned_data.get('email', '')

        # Verificar que no esté en uso (excluyendo el usuario actual)
        existentes = UserModel.objects.filter(email=email)
        if self.instance and self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso. Por favor, usa otro.')

        return email

    def save(self, commit=True):
        """
        Guarda el usuario y actualiza su perfil.

        Flujo:
        1. Guarda el modelo Usuario con los campos básicos
        2. Obtiene el Perfil asociado
        3. Actualiza los campos del Perfil
        4. Guarda el Perfil
        """
        # Guardar el usuario
        usuario = super().save(commit=False)

        if commit:
            usuario.save()

            # Actualizar el perfil
            perfil = usuario.perfil
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.direccion = self.cleaned_data.get('direccion', '')
            perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
            perfil.biografia = self.cleaned_data.get('biografia', '')

            # Manejo de foto de perfil
            foto = self.cleaned_data.get('foto_perfil')
            if foto:
                perfil.foto_perfil = foto

            perfil.save()

        return usuario


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

    biografia = forms.CharField(
        required=False,
        label='Biografía',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Cuéntanos sobre ti (opcional)',
            'rows': 4
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
            perfil.biografia = self.cleaned_data.get('biografia', '')

            # Foto de perfil
            foto = self.cleaned_data.get('foto_perfil')
            if foto:
                perfil.foto_perfil = foto

            perfil.save()

        return usuario


class GestionUsuarioForm(forms.ModelForm):
    """
    Formulario para gestión de usuarios por Superadmins.

    Diferencias con EditarPerfilForm:
    - Incluye campo is_active para activar/desactivar usuarios
    - Incluye campos is_staff y is_superuser para asignar roles
    - Validaciones adicionales para proteger roles críticos
    - NO permite cambiar contraseñas (usar sistema Django)

    Restricciones:
    - Un Superadmin puede cambiar cualquier campo excepto su propio is_superuser
    - Un Superadmin NO puede quitarse a sí mismo el rol de superadmin
    - Un Admin no puede acceder a este formulario
    """

    # Campos del modelo Usuario
    username = forms.CharField(
        required=True,
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
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

    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        }),
    )

    documento = forms.CharField(
        required=True,
        label='Documento',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Documento (10 dígitos)',
            'pattern': '[0-9]{10}',
            'maxlength': '10',
            'readonly': 'readonly'  # No permitir cambiar documento una vez creado
        }),
    )

    # Campos del modelo Perfil
    telefono = forms.CharField(
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono'
        })
    )

    direccion = forms.CharField(
        required=False,
        label='Dirección',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección'
        })
    )

    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Fecha de nacimiento'
        })
    )

    biografia = forms.CharField(
        required=False,
        label='Biografía',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Biografía del usuario',
            'rows': 4
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

    # Campos de permisos y estado
    is_active = forms.BooleanField(
        required=False,
        label='Usuario activo',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        help_text='Los usuarios inactivos no pueden iniciar sesión'
    )

    is_staff = forms.BooleanField(
        required=False,
        label='Administrador',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        help_text='Permite acceso al panel administrativo'
    )

    is_superuser = forms.BooleanField(
        required=False,
        label='Superadministrador',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        help_text='Acceso total al sistema (usar con precaución)'
    )

    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name', 'email', 'documento',
                  'is_active', 'is_staff', 'is_superuser')

    def __init__(self, *args, **kwargs):
        # Guardar referencia al usuario actual (quien está editando)
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # Si existe la instancia y tiene perfil, pre-cargar datos del perfil
        if self.instance and hasattr(self.instance, 'perfil'):
            perfil = self.instance.perfil
            self.fields['telefono'].initial = perfil.telefono
            self.fields['direccion'].initial = perfil.direccion
            self.fields['fecha_nacimiento'].initial = perfil.fecha_nacimiento
            self.fields['biografia'].initial = perfil.biografia

        # Si el usuario está editándose a sí mismo, desactivar cambio de is_superuser
        if self.instance and self.current_user and self.instance.pk == self.current_user.pk:
            self.fields['is_superuser'].widget.attrs['disabled'] = 'disabled'
            self.fields['is_superuser'].help_text = '⚠️ No puedes modificar tu propio rol de superadmin'

    def clean_username(self):
        """Validar que el username no esté en uso por otro usuario"""
        username = self.cleaned_data.get('username', '')

        # Validar longitud mínima
        if len(username) < 4:
            raise ValidationError('El nombre de usuario debe tener al menos 4 caracteres.')

        # Validar caracteres permitidos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError('El nombre de usuario solo puede contener letras, números, guiones (-) y guiones bajos (_).')

        # Verificar que no esté en uso (excluyendo el usuario actual)
        existentes = UserModel.objects.filter(username=username)
        if self.instance and self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')

        return username

    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        email = self.cleaned_data.get('email', '')

        # Verificar que no esté en uso (excluyendo el usuario actual)
        existentes = UserModel.objects.filter(email=email)
        if self.instance and self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise ValidationError('Este correo electrónico ya está en uso.')

        return email

    def clean_documento(self):
        """Validar formato del documento"""
        documento = self.cleaned_data.get('documento', '')

        if not documento.isdigit() or len(documento) != 10:
            raise ValidationError('El documento debe tener exactamente 10 dígitos.')

        # Verificar que no esté en uso (excluyendo el usuario actual)
        existentes = UserModel.objects.filter(documento=documento)
        if self.instance and self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise ValidationError('Ya existe un usuario con este documento.')

        return documento

    def clean(self):
        """Validaciones globales del formulario"""
        cleaned_data = super().clean()

        # Validación crítica: No permitir que un superadmin se quite a sí mismo el rol
        if self.instance and self.current_user and self.instance.pk == self.current_user.pk:
            # Restaurar is_superuser si intentaron cambiarlo
            if self.instance.is_superuser:
                cleaned_data['is_superuser'] = True

        # Validación: Un superadmin debe ser staff
        if cleaned_data.get('is_superuser') and not cleaned_data.get('is_staff'):
            cleaned_data['is_staff'] = True  # Auto-corregir

        # Validación: Un usuario inactivo no debe poder ser superadmin
        if not cleaned_data.get('is_active') and cleaned_data.get('is_superuser'):
            raise ValidationError(
                'Un superadministrador no puede estar inactivo. '
                'Primero quita el rol de superadmin y luego desactiva el usuario.'
            )

        return cleaned_data

    def save(self, commit=True):
        """
        Guarda el usuario y actualiza su perfil.
        """
        # Guardar el usuario
        usuario = super().save(commit=False)

        # Protección adicional: Si el usuario se está editando a sí mismo, mantener is_superuser
        if self.instance and self.current_user and self.instance.pk == self.current_user.pk:
            if self.instance.is_superuser:
                usuario.is_superuser = True

        if commit:
            usuario.save()

            # Actualizar el perfil
            perfil = usuario.perfil
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.direccion = self.cleaned_data.get('direccion', '')
            perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
            perfil.biografia = self.cleaned_data.get('biografia', '')

            # Manejo de foto de perfil
            foto = self.cleaned_data.get('foto_perfil')
            if foto:
                perfil.foto_perfil = foto

            perfil.save()

        return usuario


class LoginForm(AuthenticationForm):
    """
    Formulario de login personalizado que permite autenticación con username o documento.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario o documento'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

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

