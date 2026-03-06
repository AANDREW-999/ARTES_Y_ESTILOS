import base64

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.base import ContentFile
from django.urls import reverse_lazy
from django.views import generic

from .forms import ProductoForm
from .models import Producto


def _procesar_imagen(request, nombre_producto):
    """Procesa la imagen desde Cropper (Base64) o desde FILES."""
    cropped_data = request.POST.get('cropped_image_data', '').strip()

    if cropped_data:
        try:
            encabezado, imgstr = cropped_data.split(';base64,')
            ext = encabezado.split('/')[-1]
            nombre_archivo = f"producto_{nombre_producto}.{ext}"
            return ContentFile(base64.b64decode(imgstr), name=nombre_archivo)
        except Exception:
            pass

    return request.FILES.get('imagen') or None


class ProductoListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Producto
    template_name = "producto/lista.html"
    context_object_name = "productos"
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff


class ProductoCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "producto/form.html"
    success_url = reverse_lazy("producto:lista")
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        imagen = _procesar_imagen(self.request, form.cleaned_data.get('nombre') or 'producto')
        if imagen:
            form.instance.imagen = imagen
        messages.success(self.request, "Producto creado correctamente.")
        return super().form_valid(form)


class ProductoUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "producto/form.html"
    success_url = reverse_lazy("producto:lista")
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        imagen = _procesar_imagen(self.request, form.cleaned_data.get('nombre') or 'producto')
        if imagen:
            form.instance.imagen = imagen
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)


class ProductoDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = Producto
    template_name = "producto/detalle.html"
    context_object_name = "producto"
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff


class ProductoDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Producto
    template_name = "producto/confirm_delete.html"
    success_url = reverse_lazy("producto:lista")
    login_url = "/panel/login/"

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Producto eliminado correctamente.")
        return super().delete(request, *args, **kwargs)
