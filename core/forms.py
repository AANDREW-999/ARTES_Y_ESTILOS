from django import forms

class ContactoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Tu nombre"}
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "tucorreo@ejemplo.com"}
        ),
    )
    mensaje = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 4, "placeholder": "Cuentanos que necesitas"}
        ),
    )