from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic

from .forms import FlorForm
from .models import Flor


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
        messages.success(self.request, "Flor actualizada correctamente.")
        return super().form_valid(form)


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
