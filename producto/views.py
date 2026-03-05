from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic

from .forms import ProductoForm
from .models import Producto


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
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)


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
