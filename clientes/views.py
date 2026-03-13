from django.contrib import messages
from django.db import OperationalError, ProgrammingError, models
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import ClienteForm
from .models import Cliente
from django.http import JsonResponse
from core.notifications import crear_notificacion


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
            self.q = self.request.GET.get('q', '').strip()
            self.tipo_documento = self.request.GET.get('tipo_documento', '').strip()
            self.ciudad = self.request.GET.get('ciudad', '').strip()
            self.departamento = self.request.GET.get('departamento', '').strip()

            if self.q:
                qs = qs.filter(
                    models.Q(nombre__icontains=self.q) |
                    models.Q(apellido__icontains=self.q) |
                    models.Q(documento__icontains=self.q) |
                    models.Q(correo_electronico__icontains=self.q)
                )

            if self.tipo_documento:
                qs = qs.filter(tipo_documento=self.tipo_documento)

            if self.ciudad:
                qs = qs.filter(ciudad__icontains=self.ciudad)

            if self.departamento:
                qs = qs.filter(departamento__icontains=self.departamento)

            return qs
        except (OperationalError, ProgrammingError):
            messages.error(
                self.request,
                'La tabla de clientes no existe. Ejecuta las migraciones.'
            )
            return Cliente.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_clientes = Cliente.objects.count()
        clientes_con_correo = Cliente.objects.exclude(correo_electronico__isnull=True).exclude(correo_electronico='').count()
        clientes_con_telefono = Cliente.objects.exclude(telefono__isnull=True).exclude(telefono='').count()
        ciudades_activas = Cliente.objects.exclude(ciudad__isnull=True).exclude(ciudad='').values('ciudad').distinct().count()

        if context.get('is_paginated'):
            resultados_filtrados = context['paginator'].count
        else:
            resultados_filtrados = len(context.get('clientes', []))

        context.update({
            'query': getattr(self, 'q', ''),
            'tipo_documento_filtro': getattr(self, 'tipo_documento', ''),
            'ciudad_filtro': getattr(self, 'ciudad', ''),
            'departamento_filtro': getattr(self, 'departamento', ''),
            'tipos_documento': [
                (valor, etiqueta) for valor, etiqueta in Cliente.TIPO_DOCUMENTO_CHOICES if valor
            ],
            'ciudades_filtro': Cliente.objects.exclude(ciudad__isnull=True).exclude(ciudad='').values_list('ciudad', flat=True).distinct().order_by('ciudad'),
            'departamentos_filtro': Cliente.objects.exclude(departamento__isnull=True).exclude(departamento='').values_list('departamento', flat=True).distinct().order_by('departamento'),
            'total_clientes': total_clientes,
            'clientes_con_correo': clientes_con_correo,
            'clientes_con_telefono': clientes_con_telefono,
            'ciudades_activas': ciudades_activas,
            'resultados_filtrados': resultados_filtrados,
            'hay_filtros': any([
                getattr(self, 'q', ''),
                getattr(self, 'tipo_documento', ''),
                getattr(self, 'ciudad', ''),
                getattr(self, 'departamento', ''),
            ]),
        })
        return context


class ClienteCreateView(DBSafeMixin, generic.CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_form.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def form_valid(self, form):
        crear_notificacion(
            categoria='movimiento',
            estilo='success',
            titulo='Cliente creado',
            mensaje=f'Se creo el cliente {form.instance.nombre} {form.instance.apellido}.',
        )
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
        crear_notificacion(
            categoria='movimiento',
            estilo='info',
            titulo='Cliente actualizado',
            mensaje=f'Se actualizo el cliente {form.instance.nombre} {form.instance.apellido}.',
        )
        messages.success(self.request, 'Cliente actualizado correctamente.')
        return super().form_valid(form)


class ClienteDeleteView(DBSafeMixin, generic.DeleteView):
    model = Cliente
    template_name = 'cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:lista_clientes')

    def form_valid(self, form):
        nombre = f'{self.object.nombre} {self.object.apellido}'.strip()
        crear_notificacion(
            categoria='movimiento',
            estilo='error',
            titulo='Cliente eliminado',
            mensaje=f'Se elimino el cliente {nombre}.',
        )
        messages.success(self.request, 'Cliente eliminado correctamente.')
        return super().form_valid(form)


def verificar_documento(request):
    """Vista AJAX para verificar si un documento ya existe"""
    documento = request.GET.get('documento', '')
    exclude_id = request.GET.get('exclude_id', '')

    if not documento:
        return JsonResponse({'existe': False})

    queryset = Cliente.objects.filter(documento=documento)

    if exclude_id and exclude_id.isdigit():
        queryset = queryset.exclude(pk=int(exclude_id))

    existe = queryset.exists()
    return JsonResponse({'existe': existe})