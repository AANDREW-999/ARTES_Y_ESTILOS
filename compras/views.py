# views.py
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from .forms import CompraForm, DetalleCompraForm
from django.views import generic
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Compra, DetalleCompra
from proveedores.models import Proveedor  # Importar el modelo Proveedor

def compras_list(request):
    lista_compras = Compra.objects.all()
    template = loader.get_template('lista_compra.html')  
    
    context = {
        'compras': lista_compras,
        'total_compras': lista_compras.count()  
    }
    return HttpResponse(template.render(context, request))


def compra_detail(request, id):  
    una_compra = get_object_or_404(Compra, id=id)
    template = loader.get_template('compra_detail.html')
    
    context = {
        'compra': una_compra,
        'detalles': una_compra.detalles.all(),
    }
    return HttpResponse(template.render(context, request))

class CompraCreateView(generic.CreateView):
    """Vista para crear una nueva compra"""
    model = Compra
    form_class = CompraForm
    template_name = 'crear_compra.html'
    success_url = reverse_lazy('compras:lista_compra')
    
    def get_context_data(self, **kwargs):
        """Agregar proveedores al contexto"""
        context = super().get_context_data(**kwargs)
        context['proveedores'] = Proveedor.objects.filter(activo=True).order_by('nombre_proveedor')
        return context
    
    def form_valid(self, form):
        """Procesar la compra y sus detalles"""
        try:
            # Guardar la compra primero
            compra = form.save(commit=False)
            # Inicializar totales con valores por defecto
            compra.subtotal = 0
            compra.total_compra = 0
            compra.save()
            
            # Obtener los arrays del POST
            rifs = self.request.POST.getlist('rif[]')
            precios = self.request.POST.getlist('precio[]')
            cantidades = self.request.POST.getlist('cantidad[]')
            
            # Crear DetalleCompra para cada artículo
            detalle_count = 0
            for rif, precio, cantidad in zip(rifs, precios, cantidades):
                # Validar que no esté vacío
                if precio and cantidad:
                    try:
                        # Limpiar el precio: remover puntos (miles) y reemplazar coma por punto
                        precio_limpio = str(precio).replace('.', '').replace(',', '.')
                        cantidad_limpia = str(cantidad).strip()
                        
                        detalle = DetalleCompra(
                            compra=compra,
                            rif=rif if rif else '',
                            precio=float(precio_limpio),
                            cantidad=int(cantidad_limpia)
                        )
                        detalle.save()
                        detalle_count += 1
                    except (ValueError, TypeError) as e:
                        print(f"Error en detalle {detalle_count}: {e}, precio='{precio}', cantidad='{cantidad}'")
                        compra.delete()
                        messages.error(
                            self.request,
                            f'Error al procesar artículo: formato inválido. Asegúrese de que los valores sean correctos.'
                        )
                        return self.form_invalid(form)
            
            if detalle_count == 0:
                compra.delete()
                messages.error(
                    self.request,
                    'Debe agregar al menos un artículo a la compra.'
                )
                return self.form_invalid(form)
            
            # Calcular totales
            compra.calcular_totales()
            
            messages.success(
                self.request,
                f'¡Compra registrada exitosamente! {detalle_count} artículo{"s" if detalle_count != 1 else ""} agregado{"s" if detalle_count != 1 else ""}.'
            )
            return redirect(self.success_url)
        except Exception as e:
            print(f"Error inesperado en form_valid: {e}")
            messages.error(
                self.request,
                f'Error al guardar la compra: {str(e)}'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CompraUpdateView(generic.UpdateView):
    """Vista para actualizar una compra existente"""
    model = Compra
    form_class = CompraForm
    template_name = 'editar_compra.html'
    success_url = reverse_lazy('compras:lista_compra')
    pk_url_kwarg = 'compra_id'
    
    def get_context_data(self, **kwargs):
        """Agregar proveedores y detalles al contexto para edición"""
        context = super().get_context_data(**kwargs)
        context['proveedores'] = Proveedor.objects.filter(activo=True).order_by('nombre_proveedor')
        context['detalles'] = self.object.detalles.all()
        return context
    
    def form_valid(self, form):
        # Guardar la compra
        compra = form.save()
        
        # Obtener los arrays del POST
        rifs = self.request.POST.getlist('rif[]')
        precios = self.request.POST.getlist('precio[]')
        cantidades = self.request.POST.getlist('cantidad[]')
        
        # Limpiar detalles anteriores
        compra.detalles.all().delete()
        
        # Crear DetalleCompra para cada artículo
        for rif, precio, cantidad in zip(rifs, precios, cantidades):
            if precio and cantidad:
                try:
                    detalle = DetalleCompra(
                        compra=compra,
                        rif=rif if rif else '',
                        precio=float(precio.replace('.', '').replace(',', '.')) if precio else 0,
                        cantidad=int(cantidad)
                    )
                    detalle.save()
                except (ValueError, TypeError) as e:
                    print(f"Error procesando detalle: {e}")
                    messages.error(
                        self.request,
                        f'Error al procesar los artículos. Asegúrese de que los valores sean correctos.'
                    )
                    return self.form_invalid(form)
        
        # Calcular totales
        compra.calcular_totales()
        
        messages.success(
            self.request,
            f'La compra ha sido actualizada exitosamente.'
        )
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CompraDeleteView(generic.DeleteView):
    """Vista para eliminar una compra"""
    model = Compra
    template_name = 'eliminar_compra.html'
    success_url = reverse_lazy('compras:lista_compra')
    pk_url_kwarg = 'compra_id'
    
    def delete(self, request, *args, **kwargs):
        compra = self.get_object()
        messages.success(
            request,
            f'La compra {compra.descripcion} ha sido eliminada exitosamente.'
        )
        return super().delete(request, *args, **kwargs)