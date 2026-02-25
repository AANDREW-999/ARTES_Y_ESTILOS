from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Perfil

User = get_user_model()


# =====================================================
# 🔐 LOGIN FORM
# =====================================================

class LoginForm(AuthenticationForm):

    def clean(self):
        username_or_doc = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if not username_or_doc or not password:
            raise ValidationError("Usuario/documento y contraseña son obligatorios.")

        if username_or_doc.isdigit() and len(username_or_doc) == 10:
            try:
                user_obj = User.objects.get(documento=username_or_doc)
                user = authenticate(self.request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(self.request, username=username_or_doc, password=password)

        if user is None:
            raise ValidationError("Credenciales inválidas.")

        self.confirm_login_allowed(user)
        self.user_cache = user
        return self.cleaned_data


# =====================================================
# 📝 REGISTRO FORM (Usuario + Perfil)
# =====================================================

class RegistroForm(UserCreationForm):

    # Campos del Perfil
    telefono         = forms.CharField(required=False, label="Teléfono")
    direccion        = forms.CharField(required=False, label="Dirección")
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    biografia   = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False, label="Biografía")
    foto_perfil = forms.ImageField(required=False, label="Foto de perfil")

    class Meta:
        model = User
        fields = (
            "username",
            "documento",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean_documento(self):
        documento = self.cleaned_data.get("documento", "")
        if not documento or not documento.isdigit() or len(documento) != 10:
            raise ValidationError("El documento debe tener exactamente 10 dígitos.")
        if User.objects.filter(documento=documento).exists():
            raise ValidationError("Este documento ya está registrado.")
        return documento


# =====================================================
# ✏️ EDITAR PERFIL / USUARIO FORM
# =====================================================

class EditarPerfilForm(forms.ModelForm):
    """
    Formulario unificado para editar Usuario + Perfil.

    Campos del modelo Usuario: first_name, last_name, username,
        email, documento, is_active, is_staff, is_superuser.

    Campos del modelo Perfil (inyectados como extra fields):
        telefono, direccion, fecha_nacimiento, biografia, foto_perfil.
    """

    # ── Campos extra del Perfil (no están en User) ──────────────────────
    telefono = forms.CharField(
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={"placeholder": "Ej: 3001234567"}),
    )
    direccion = forms.CharField(
        required=False,
        label="Dirección",
        widget=forms.TextInput(attrs={"placeholder": "Dirección completa"}),
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    biografia = forms.CharField(
        required=False,
        label="Biografía",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Cuéntanos algo sobre ti..."}),
    )
    foto_perfil = forms.ImageField(
        required=False,
        label="Foto de perfil",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "documento",      # ← campo del modelo Usuario — era la causa del error
            "is_active",      # ← necesario porque el template usa {{ form.is_active }}
            "is_staff",
            "is_superuser",
        ]

    def __init__(self, *args, **kwargs):
        self.editing_user = kwargs.pop("editing_user", None)
        super().__init__(*args, **kwargs)

        # Cargar valores actuales del Perfil relacionado
        if self.instance.pk:
            try:
                perfil = self.instance.perfil
                self.fields["telefono"].initial          = perfil.telefono
                self.fields["direccion"].initial          = perfil.direccion
                self.fields["fecha_nacimiento"].initial   = perfil.fecha_nacimiento
                self.fields["biografia"].initial          = perfil.biografia
                self.fields["foto_perfil"].initial        = perfil.foto_perfil
            except Perfil.DoesNotExist:
                pass

    # ── Validaciones ─────────────────────────────────────────────────────

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean_documento(self):
        documento = self.cleaned_data.get("documento", "")
        if not documento or not documento.isdigit() or len(documento) != 10:
            raise ValidationError("El documento debe tener exactamente 10 dígitos.")
        qs = User.objects.filter(documento=documento)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este documento ya está registrado.")
        return documento

    # ── Guardado atómico: User + Perfil ──────────────────────────────────

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=commit)

            perfil = user.perfil
            perfil.telefono          = self.cleaned_data.get("telefono", "")
            perfil.direccion          = self.cleaned_data.get("direccion", "")
            perfil.fecha_nacimiento   = self.cleaned_data.get("fecha_nacimiento")
            perfil.biografia          = self.cleaned_data.get("biografia", "")

            foto = self.cleaned_data.get("foto_perfil")
            # Solo actualizar si es un archivo subido nuevo (no el string del initial)
            if foto and hasattr(foto, "name"):
                perfil.foto_perfil = foto

            if commit:
                perfil.save()

        return user