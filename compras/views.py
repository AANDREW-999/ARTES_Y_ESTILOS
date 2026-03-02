# views.py
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from .forms import CompraForm, DetalleCompraForm
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Compra, DetalleCompra
from proveedores.models import Proveedor  # Importar el modelo Proveedor
from django.db.models import Q, Sum, Count
from datetime import datetime, date

def compras_list(request):
    # Optimizar queries con select_related y prefetch_related
    lista_compras = Compra.objects.select_related(
        'proveedor',
        'usuario'
    ).prefetch_related('detalles').all()
    
    # Aplicar filtros si existen
    proveedor_nombre = request.GET.get('proveedor_nombre', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '')
    
    if proveedor_nombre:
        lista_compras = lista_compras.filter(proveedor__nombre_proveedor__icontains=proveedor_nombre)
    
    if fecha_desde:
        try:
            fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            lista_compras = lista_compras.filter(fecha_emision__gte=fecha)
        except:
            fecha_desde = ''
    template = loader.get_template('lista_compra.html')  
    
    # Obtener proveedores para el datalist (ordenado por nombre)
    proveedores = Proveedor.objects.all().order_by('nombre_proveedor')
    
    # Calcular estadísticas
    total_compras = lista_compras.count()
    monto_total = lista_compras.aggregate(Sum('total_compra'))['total_compra__sum'] or 0
    total_proveedores = lista_compras.values('proveedor').distinct().count()
    
    # Compras de este mes
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    compras_mes = lista_compras.filter(
        fecha_emision__gte=inicio_mes,
        fecha_emision__lte=hoy
    ).count()
    
    context = {
        'compras': lista_compras,
        'total_compras': total_compras,
        'monto_total': monto_total,
        'total_proveedores': total_proveedores,
        'compras_mes': compras_mes,
        'proveedores': proveedores,
        'proveedor_nombre_filtro': proveedor_nombre,
        'fecha_desde_filtro': fecha_desde,
    }
    return HttpResponse(template.render(context, request))

def form_invalid(self, form):
    print("ERRORES:", form.errors.as_json())
    messages.error(self.request, f'Errores del form: {form.errors}')
    return super().form_invalid(form)


def compra_detail(request, id):  
    una_compra = get_object_or_404(
        Compra.objects.select_related('proveedor', 'usuario').prefetch_related('detalles'),
        id=id
    )
    template = loader.get_template('compra_detail.html')
    
    context = {
        'compra': una_compra,
        'detalles': una_compra.detalles.all(),
    }
    return HttpResponse(template.render(context, request))

class CompraCreateView(LoginRequiredMixin, generic.CreateView):
    """Vista para crear una nueva compra"""
    model = Compra
    form_class = CompraForm
    template_name = 'crear_compra.html'
    success_url = reverse_lazy('compras:lista_compra')
    login_url = 'usuarios:login'
    
    def get_context_data(self, **kwargs):
        """Agregar proveedores al contexto"""
        context = super().get_context_data(**kwargs)
        context['proveedores'] = Proveedor.objects.filter(activo=True).order_by('nombre_proveedor')
        return context
    
    def form_valid(self, form):
        """Procesar la compra y sus detalles"""
        try:
            # Obtener los arrays del POST primero para validar
            rifs = self.request.POST.getlist('rif[]')
            precios = self.request.POST.getlist('precio[]')
            cantidades = self.request.POST.getlist('cantidad[]')
            
            # Filtrar los detalles vacíos y validar
            detalles_validos = []
            for idx, (rif, precio, cantidad) in enumerate(zip(rifs, precios, cantidades)):
                precio_str = str(precio).strip()
                cantidad_str = str(cantidad).strip()
                
                # Saltar filas completamente vacías
                if not precio_str and not cantidad_str:
                    continue
                    
                # Validar que tenga precio y cantidad
                if not precio_str or not cantidad_str:
                    messages.error(
                        self.request,
                        f'Artículo {idx + 1}: Debe completar tanto precio como cantidad.'
                    )
                    return self.form_invalid(form)
                
                try:
                    # Limpiar el precio: remover puntos (miles) y reemplazar coma por punto
                    precio_limpio = precio_str.replace('.', '').replace(',', '.')
                    cantidad_limpia = int(cantidad_str)
                    
                    if float(precio_limpio) <= 0:
                        messages.error(
                            self.request,
                            f'Artículo {idx + 1}: El precio debe ser mayor a 0.'
                        )
                        return self.form_invalid(form)
                    
                    if cantidad_limpia <= 0:
                        messages.error(
                            self.request,
                            f'Artículo {idx + 1}: La cantidad debe ser mayor a 0.'
                        )
                        return self.form_invalid(form)
                    
                    detalles_validos.append((rif.strip() if rif else '', precio_limpio, cantidad_limpia))
                    
                except (ValueError, TypeError) as e:
                    messages.error(
                        self.request,
                        f'Artículo {idx + 1}: Formato inválido. Verifique precio y cantidad.'
                    )
                    return self.form_invalid(form)
            
            # Validar que haya al menos un artículo
            if not detalles_validos:
                messages.error(
                    self.request,
                    'Debe agregar al menos un artículo con precio y cantidad válidos.'
                )
                return self.form_invalid(form)
            
            # Guardar la compra
            compra = form.save(commit=False)
            compra.subtotal = 0
            compra.total_compra = 0
            compra.usuario = self.request.user
            compra.save()
            
            # Crear los detalles validados
            for rif, precio_limpio, cantidad in detalles_validos:
                detalle = DetalleCompra(
                    compra=compra,
                    rif=rif,
                    precio=float(precio_limpio),
                    cantidad=cantidad
                )
                detalle.save()
            
            # Calcular totales
            compra.calcular_totales()
            
            messages.success(
                self.request,
                f'¡Compra registrada exitosamente! {len(detalles_validos)} artículo{"s" if len(detalles_validos) != 1 else ""} agregado{"s" if len(detalles_validos) != 1 else ""}.'
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


class CompraUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Vista para actualizar una compra existente"""
    model = Compra
    form_class = CompraForm
    template_name = 'editar_compra.html'
    success_url = reverse_lazy('compras:lista_compra')
    pk_url_kwarg = 'compra_id'
    login_url = 'usuarios:login'
    
    def get_context_data(self, **kwargs):
        """Agregar proveedores y detalles al contexto para edición"""
        context = super().get_context_data(**kwargs)
        context['proveedores'] = Proveedor.objects.filter(activo=True).order_by('nombre_proveedor')
        context['detalles'] = self.object.detalles.all()
        return context
    
    def form_valid(self, form):
        """Procesar la actualización de compra y sus detalles"""
        try:
            # Obtener los arrays del POST para validar
            rifs = self.request.POST.getlist('rif[]')
            precios = self.request.POST.getlist('precio[]')
            cantidades = self.request.POST.getlist('cantidad[]')
            
            # Filtrar los detalles vacíos y validar
            detalles_validos = []
            for idx, (rif, precio, cantidad) in enumerate(zip(rifs, precios, cantidades)):
                precio_str = str(precio).strip()
                cantidad_str = str(cantidad).strip()
                
                # Saltar filas completamente vacías
                if not precio_str and not cantidad_str:
                    continue
                    
                # Validar que tenga precio y cantidad
                if not precio_str or not cantidad_str:
                    messages.error(
                        self.request,
                        f'Artículo {idx + 1}: Debe completar tanto precio como cantidad.'
                    )
                    return self.form_invalid(form)
                
                try:
                    # Limpiar el precio
                    precio_limpio = precio_str.replace('.', '').replace(',', '.')
                    cantidad_limpia = int(cantidad_str)
                    
                    if float(precio_limpio) <= 0:
                        messages.error(
                            self.request,
                            f'Artículo {idx + 1}: El precio debe ser mayor a 0.'
                        )
                        return self.form_invalid(form)
                    
                    if cantidad_limpia <= 0:
                        messages.error(
                            self.request,
                            f'Artículo {idx + 1}: La cantidad debe ser mayor a 0.'
                        )
                        return self.form_invalid(form)
                    
                    detalles_validos.append((rif.strip() if rif else '', precio_limpio, cantidad_limpia))
                    
                except (ValueError, TypeError) as e:
                    messages.error(
                        self.request,
                        f'Artículo {idx + 1}: Formato inválido. Verifique precio y cantidad.'
                    )
                    return self.form_invalid(form)
            
            # Validar que haya al menos un artículo
            if not detalles_validos:
                messages.error(
                    self.request,
                    'Debe agregar al menos un artículo con precio y cantidad válidos.'
                )
                return self.form_invalid(form)
            
            # Guardar la compra
            compra = form.save()
            
            # Limpiar detalles anteriores y crear los nuevos
            compra.detalles.all().delete()
            
            for rif, precio_limpio, cantidad in detalles_validos:
                detalle = DetalleCompra(
                    compra=compra,
                    rif=rif,
                    precio=float(precio_limpio),
                    cantidad=cantidad
                )
                detalle.save()
            
            # Calcular totales
            compra.calcular_totales()
            
            messages.success(
                self.request,
                f'¡Compra actualizada exitosamente! {len(detalles_validos)} artículo{"s" if len(detalles_validos) != 1 else ""}.'
            )
            return redirect(self.success_url)
        except Exception as e:
            print(f"Error inesperado en form_valid: {e}")
            messages.error(
                self.request,
                f'Error al actualizar la compra: {str(e)}'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CompraDeleteView(LoginRequiredMixin, generic.DeleteView):
    """Vista para eliminar una compra"""
    model = Compra
    template_name = 'eliminar_compra.html'
    success_url = reverse_lazy('compras:lista_compra')
    pk_url_kwarg = 'compra_id'
    login_url = 'usuarios:login'
    
    def delete(self, request, *args, **kwargs):
        compra = self.get_object()
        messages.success(
            request,
            f'La compra {compra.descripcion} ha sido eliminada exitosamente.'
        )
        return super().delete(request, *args, **kwargs)
        return super().delete(request, *args, **kwargs)