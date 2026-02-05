from django.contrib import messages
from django.db import OperationalError, ProgrammingError, models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
import json
from django.conf import settings
from pathlib import Path

from .forms import ClienteForm
from .models import Cliente


# -------------------------
# Mixin de seguridad DB
# -------------------------
class DBSafeMixin:
    """Mixin que captura errores de base de datos y redirige con instrucción para aplicar migraciones.
    No altera la lógica de las vistas; solo evita 500s en entornos sin migraciones aplicadas.
    """
    def dispatch(self, request, *args, **kwargs):
        base = super()
        dispatch_method = getattr(base, 'dispatch', None)
        try:
            if dispatch_method:
                return dispatch_method(request, *args, **kwargs)
        except (OperationalError, ProgrammingError):
            messages.error(request, 'La tabla de clientes no existe. Ejecuta: python manage.py makemigrations clientes && python manage.py migrate')
            return redirect(reverse_lazy('clientes:lista_clientes'))

        # Si no existe dispatch en la clase base, informar y redirigir de forma segura
        messages.error(request, 'La vista no está disponible en este contexto.')
        return redirect(reverse_lazy('clientes:lista_clientes'))


# -------------------------
# Cargar mapeo de ciudades (id -> nombre) basándose en el JSON estático.
# Usamos la misma fórmula de generación de ids que en el JS: id = (dept_index * 2000) + i + 1
CITY_ID_MAP = {}

def build_city_id_map():
    global CITY_ID_MAP
    if CITY_ID_MAP:
        return CITY_ID_MAP
    try:
        data_path = Path(settings.BASE_DIR) / 'clientes' / 'static' / 'clientes' / 'data' / 'colombia_municipios.json'
        if not data_path.exists():
            return {}
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        CITY_ID_MAP = {}
        # Mantener el orden de departamentos tal como aparece en el JSON
        for dept_idx, (dept_name, cities) in enumerate(data.items()):
            if not isinstance(cities, list):
                continue
            for i, city in enumerate(cities):
                # city puede ser string o un objeto; manejar string
                city_name = city if isinstance(city, str) else (city.get('name') or city.get('nombre') or city.get('municipio'))
                cid = dept_idx * 2000 + i + 1
                CITY_ID_MAP[cid] = city_name
    except Exception:
        CITY_ID_MAP = {}
    return CITY_ID_MAP


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
            messages.error(self.request, 'La tabla de clientes no existe. Ejecuta: python manage.py makemigrations clientes && python manage.py migrate')
            return Cliente.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        # Añadir nombre de ciudad a cada cliente para mostrar en la plantilla
        city_map = build_city_id_map()
        for cliente in context.get('clientes', []):
            try:
                cliente.ciudad_nombre = city_map.get(int(cliente.ciudad_id)) if cliente.ciudad_id else ''
            except Exception:
                cliente.ciudad_nombre = ''
        return context


class ClienteCreateView(DBSafeMixin, generic.CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_form.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def form_valid(self, form):
        try:
            messages.success(self.request, 'Cliente creado correctamente.')
            return super().form_valid(form)
        except (OperationalError, ProgrammingError):
            messages.error(self.request, 'No se pudo crear el cliente porque la tabla no existe. Ejecuta las migraciones.')
            return redirect(self.success_url)


class ClienteDetailView(DBSafeMixin, generic.DetailView):
    model = Cliente
    template_name = 'cliente_detail.html'
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_map = build_city_id_map()
        cliente = context.get('cliente')
        if cliente:
            try:
                cliente.ciudad_nombre = city_map.get(int(cliente.ciudad_id)) if cliente.ciudad_id else ''
            except Exception:
                cliente.ciudad_nombre = ''
        return context


class ClienteUpdateView(DBSafeMixin, generic.UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_form.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def form_valid(self, form):
        try:
            messages.success(self.request, 'Cliente actualizado correctamente.')
            return super().form_valid(form)
        except (OperationalError, ProgrammingError):
            messages.error(self.request, 'No se pudo actualizar el cliente porque la tabla no existe. Ejecuta las migraciones.')
            return redirect(self.success_url)


class ClienteDeleteView(DBSafeMixin, generic.DeleteView):
    model = Cliente
    template_name = 'cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(self.request, 'Cliente eliminado correctamente.')
            return super().delete(request, *args, **kwargs)
        except (OperationalError, ProgrammingError):
            messages.error(self.request, 'No se pudo eliminar el cliente porque la tabla no existe. Ejecuta las migraciones.')
            return redirect(self.success_url)
