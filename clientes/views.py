from django.contrib import messages
from django.db import OperationalError, ProgrammingError, models
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import ClienteForm
from .models import Cliente


# -------------------------
# Mixin de seguridad DB
# -------------------------
class DBSafeMixin:
    """
    Mixin que captura errores de base de datos y redirige con instrucción
    para aplicar migraciones, evitando errores 500.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except (OperationalError, ProgrammingError):
            messages.error(
                request,
                'La tabla de clientes no existe. Ejecuta: '
                'python manage.py makemigrations clientes && python manage.py migrate'
            )
            return redirect(reverse_lazy('clientes:lista_clientes'))


# -------------------------
# Vistas CRUD para Cliente
# -------------------------
class ClienteListView(generic.ListView):
    model = Cliente
    template_name = 'lista_clientes.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        try:
            qs = super().get_queryset()
            q = self.request.GET.get('q')
            if q:
                qs = qs.filter(
                    models.Q(nombre__icontains=q) |
                    models.Q(apellido__icontains=q) |
                    models.Q(documento__icontains=q)
                )
            return qs
        except (OperationalError, ProgrammingError):
            messages.error(
                self.request,
                'La tabla de clientes no existe. Ejecuta las migraciones.'
            )
            return Cliente.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class ClienteCreateView(DBSafeMixin, generic.CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_form.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente creado correctamente.')
        return super().form_valid(form)


class ClienteDetailView(DBSafeMixin, generic.DetailView):
    model = Cliente
    template_name = 'cliente_detail.html'
    context_object_name = 'cliente'


class ClienteUpdateView(DBSafeMixin, generic.UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_form.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado correctamente.')
        return super().form_valid(form)


class ClienteDeleteView(DBSafeMixin, generic.DeleteView):
    model = Cliente
    template_name = 'cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Cliente eliminado correctamente.')
        return super().delete(request, *args, **kwargs)
