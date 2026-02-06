# views.py
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from .forms import CompraForm
from django.views import generic
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Compra

def compras_list(request):
    lista_de_compras = Compra.objects.all()
    template = loader.get_template('all_compra.html')  
    
    context = {
        'compras': lista_de_compras,
        'total_compras': lista_de_compras.count()  
    }
    return HttpResponse(template.render(context, request))

def compra_detail(request, id):  
    una_compra = get_object_or_404(Compra, id=id)
    template = loader.get_template('compra_detail.html')
    
    context = {
        'compra': una_compra,
    }
    return HttpResponse(template.render(context, request))

class CompraCreateView(generic.CreateView):
    """Vista para crear una nueva compra"""
    model = Compra
    form_class = CompraForm
    template_name = 'crear_compra.html'
    success_url = reverse_lazy('compras:compras_list')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f'La compra {form.instance.descripcion} ha sido registrada exitosamente.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CompraUpdateView(generic.UpdateView):
    """Vista para actualizar una compra existente"""
    model = Compra
    form_class = CompraForm
    template_name = 'editar_compra.html'
    success_url = reverse_lazy('compras:compras_list')
    pk_url_kwarg = 'compra_id'
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f'La compra {form.instance.descripcion} ha sido actualizada exitosamente.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CompraDeleteView(generic.DeleteView):
    """Vista para eliminar una compra"""
    model = Compra
    template_name = 'eliminar_compra.html'
    success_url = reverse_lazy('compras:compras_list')
    pk_url_kwarg = 'compra_id'
    
    def delete(self, request, *args, **kwargs):
        compra = self.get_object()
        messages.success(
            request,
            f'La compra {compra.descripcion} ha sido eliminada exitosamente.'
        )
        return super().delete(request, *args, **kwargs)