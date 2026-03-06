import base64
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.base import ContentFile
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views import generic

from .forms import FlorForm
from .models import Flor


def _parse_decimal(valor):
    if valor is None:
        return None

    limpio = str(valor).strip()
    if not limpio:
        return None

    normalizado = limpio.replace('.', '').replace(',', '.')
    try:
        return Decimal(normalizado)
    except (InvalidOperation, ValueError):
        return None


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

    def get_queryset(self):
        queryset = Flor.objects.all()

        self.q = self.request.GET.get('q', '').strip()
        self.tipo = self.request.GET.get('tipo', '').strip()
        self.nivel_stock = self.request.GET.get('nivel_stock', '').strip()
        self.precio_min_raw = self.request.GET.get('precio_min', '').strip()
        self.precio_max_raw = self.request.GET.get('precio_max', '').strip()

        if self.q:
            queryset = queryset.filter(
                Q(nombre__icontains=self.q) |
                Q(descripcion__icontains=self.q) |
                Q(tipo_flor__icontains=self.q)
            )

        if self.tipo:
            queryset = queryset.filter(tipo_flor=self.tipo)

        if self.nivel_stock == 'bajo':
            queryset = queryset.filter(cantidad__lte=10)
        elif self.nivel_stock == 'medio':
            queryset = queryset.filter(cantidad__gte=11, cantidad__lte=30)
        elif self.nivel_stock == 'alto':
            queryset = queryset.filter(cantidad__gt=30)

        precio_min = _parse_decimal(self.precio_min_raw)
        precio_max = _parse_decimal(self.precio_max_raw)

        if precio_min is not None and precio_max is not None and precio_min > precio_max:
            precio_min, precio_max = precio_max, precio_min
            self.precio_min_raw = str(precio_min)
            self.precio_max_raw = str(precio_max)
            messages.info(self.request, 'Se ajusto el rango de precios porque el minimo era mayor al maximo.')

        if precio_min is not None:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max is not None:
            queryset = queryset.filter(precio__lte=precio_max)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_flores = Flor.objects.count()
        total_stock = Flor.objects.aggregate(total=Sum('cantidad'))['total'] or 0
        bajo_stock = Flor.objects.filter(cantidad__lte=10).count()
        tipos_usados = Flor.objects.values('tipo_flor').distinct().count()

        context.update({
            'busqueda': getattr(self, 'q', ''),
            'tipo_filtro': getattr(self, 'tipo', ''),
            'nivel_stock_filtro': getattr(self, 'nivel_stock', ''),
            'precio_min_filtro': getattr(self, 'precio_min_raw', ''),
            'precio_max_filtro': getattr(self, 'precio_max_raw', ''),
            'tipos_filtro': Flor._meta.get_field('tipo_flor').choices,
            'total_flores': total_flores,
            'total_stock': total_stock,
            'bajo_stock': bajo_stock,
            'tipos_usados': tipos_usados,
            'resultados_filtrados': context['flores'].count(),
            'hay_filtros': any([
                getattr(self, 'q', ''),
                getattr(self, 'tipo', ''),
                getattr(self, 'nivel_stock', ''),
                getattr(self, 'precio_min_raw', ''),
                getattr(self, 'precio_max_raw', ''),
            ]),
        })
        return context


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
