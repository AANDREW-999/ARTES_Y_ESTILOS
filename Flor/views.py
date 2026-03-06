import base64

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.base import ContentFile
from django.urls import reverse_lazy
from django.views import generic

from .forms import FlorForm
from .models import Flor


def _procesar_imagen(request, nombre_flor):
    """Procesa la imagen desde Cropper (Base64) o desde FILES."""
    cropped_data = request.POST.get('cropped_image_data', '').strip()

    if cropped_data:
        try:
            encabezado, imgstr = cropped_data.split(';base64,')
            ext = encabezado.split('/')[-1]
            nombre_archivo = f"flor_{nombre_flor}.{ext}"
            return ContentFile(base64.b64decode(imgstr), name=nombre_archivo)
        except Exception:
            pass

    return request.FILES.get('imagen') or None


class FlorListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Flor
    template_name = "flor/lista.html"
    context_object_name = "flores"
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff


class FlorCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Flor
    form_class = FlorForm
    template_name = "flor/form.html"
    success_url = reverse_lazy("flor:lista")
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        imagen = _procesar_imagen(self.request, form.cleaned_data.get('nombre') or 'flor')
        if imagen:
            form.instance.imagen = imagen
        messages.success(self.request, "Flor creada correctamente.")
        return super().form_valid(form)


class FlorUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Flor
    form_class = FlorForm
    template_name = "flor/form.html"
    success_url = reverse_lazy("flor:lista")
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        imagen = _procesar_imagen(self.request, form.cleaned_data.get('nombre') or 'flor')
        if imagen:
            form.instance.imagen = imagen
        messages.success(self.request, "Flor actualizada correctamente.")
        return super().form_valid(form)


class FlorDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = Flor
    template_name = "flor/detalle.html"
    context_object_name = "flor"
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff


class FlorDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Flor
    template_name = "flor/confirm_delete.html"
    success_url = reverse_lazy("flor:lista")
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Flor eliminada correctamente.")
        return super().delete(request, *args, **kwargs)
