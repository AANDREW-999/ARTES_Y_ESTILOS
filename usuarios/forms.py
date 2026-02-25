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
    telefono = forms.CharField(required=False)
    direccion = forms.CharField(required=False)
    fecha_nacimiento = forms.DateField(required=False)
    biografia = forms.CharField(widget=forms.Textarea, required=False)
    foto_perfil = forms.ImageField(required=False)

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

    # ---------------- VALIDACIONES ---------------- #

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean_documento(self):
        documento = self.cleaned_data.get("documento")

        if not documento.isdigit() or len(documento) != 10:
            raise ValidationError("El documento debe tener exactamente 10 dígitos.")

        qs = User.objects.filter(documento=documento)
        if qs.exists():
            raise ValidationError("Este documento ya está registrado.")
        return documento


# =====================================================
# ✏️ EDITAR PERFIL FORM (Usuario + Perfil)
# =====================================================

class EditarPerfilForm(forms.ModelForm):

    # Campos del Perfil
    telefono = forms.CharField(required=False)
    direccion = forms.CharField(required=False)
    fecha_nacimiento = forms.DateField(required=False)
    biografia = forms.CharField(widget=forms.Textarea, required=False)
    foto_perfil = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        self.editing_user = kwargs.pop("editing_user", None)
        super().__init__(*args, **kwargs)

        # Cargar datos iniciales del perfil
        if self.instance.pk:
            perfil = self.instance.perfil
            self.fields["telefono"].initial = perfil.telefono
            self.fields["direccion"].initial = perfil.direccion
            self.fields["fecha_nacimiento"].initial = perfil.fecha_nacimiento
            self.fields["biografia"].initial = perfil.biografia
            self.fields["foto_perfil"].initial = perfil.foto_perfil

    # ---------------- VALIDACIONES ---------------- #

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
        documento = self.cleaned_data.get("documento")

        if not documento.isdigit() or len(documento) != 10:
            raise ValidationError("El documento debe tener exactamente 10 dígitos.")

        qs = User.objects.filter(documento=documento)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Este documento ya está registrado.")
        return documento

    # ---------------- SAVE PROFESIONAL ---------------- #

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=commit)

            perfil = user.perfil
            perfil.telefono = self.cleaned_data.get("telefono")
            perfil.direccion = self.cleaned_data.get("direccion")
            perfil.fecha_nacimiento = self.cleaned_data.get("fecha_nacimiento")
            perfil.biografia = self.cleaned_data.get("biografia")

            foto = self.cleaned_data.get("foto_perfil")
            if foto:
                perfil.foto_perfil = foto

            if commit:
                perfil.save()

        return user