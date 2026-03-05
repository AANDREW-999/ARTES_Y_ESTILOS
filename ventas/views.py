from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import Venta, DetalleVenta
from .forms import VentaForm
from clientes.models import Cliente
from flor.models import Flor
from producto.models import Producto


def listar_ventas(request):
    ventas = Venta.objects.select_related('cliente').prefetch_related('detalles__flor', 'detalles__producto')
    return render(request, 'ventas/listar_venta.html', {'ventas': ventas})


@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)

        arreglo_ids = request.POST.getlist('arreglo_id[]')
        cantidades  = request.POST.getlist('cantidad[]')
        precios     = request.POST.getlist('precio[]')

        items_validos = [
            (aid, cant, prec)
            for aid, cant, prec in zip(arreglo_ids, cantidades, precios)
            if aid
        ]

        if not items_validos:
            messages.error(request, 'Debes agregar al menos un ítem a la venta.')
        elif form.is_valid():
            venta = form.save(commit=False)
            venta.total = Decimal('0')
            venta.save()

            for aid, cant, prec in items_validos:
                try:
                    # aid viene como "F-<id>" o "P-<id>" desde el autocomplete
                    tipo, raw_id = (aid or '').split('-', 1)
                    item_id = int(raw_id)

                    if tipo == 'F':
                        DetalleVenta.objects.create(
                            venta=venta,
                            tipo_item='FLOR',
                            flor_id=item_id,
                            cantidad=int(cant),
                            precio=Decimal(prec),
                        )
                    elif tipo == 'P':
                        DetalleVenta.objects.create(
                            venta=venta,
                            tipo_item='PRODUCTO',
                            producto_id=item_id,
                            cantidad=int(cant),
                            precio=Decimal(prec),
                        )
                    else:
                        continue
                except (ValueError, Exception):
                    pass

            venta.recalcular_totales()
            venta.save(update_fields=['subtotal_sin_iva', 'iva_monto', 'total'])

            messages.success(request, f'Venta #{venta.id} registrada correctamente.')
            return redirect('ventas:listar_venta')

    else:
        form = VentaForm()

    return render(request, 'ventas/agregar_venta.html', {'form': form})


def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            return redirect('ventas:listar_venta')
    else:
        form = VentaForm(instance=venta)

    return render(request, 'ventas/editar_venta.html', {'form': form, 'venta': venta})


def detalle_venta(request, pk):
    venta = get_object_or_404(
        Venta.objects.prefetch_related('detalles__flor', 'detalles__producto').select_related('cliente'),
        pk=pk
    )
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})


def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == 'POST':
        venta.delete()
        return redirect('ventas:listar_venta')

    return render(request, 'ventas/eliminar_venta.html', {'venta': venta})


def buscar_cliente(request):
    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.filter(nombre__icontains=q)[:10]
    data = list(clientes.values('id', 'nombre', 'direccion'))
    return JsonResponse({'clientes': data})

def buscar_arreglo(request):
    q = request.GET.get('q', '').strip()

    flores = Flor.objects.filter(nombre__icontains=q)[:10]
    productos = Producto.objects.filter(nombre__icontains=q)[:10]

    data = []
    for f in flores:
        data.append({
            'id': f'F-{f.id}',
            'nombre_flor': f.nombre,
            'tipo_producto': 'Flor',
            'descripcion': f.descripcion,
            'precio': str(f.precio),
            'imagen': f.imagen.url if f.imagen else '',
        })

    for p in productos:
        data.append({
            'id': f'P-{p.id}',
            'nombre_flor': p.nombre,
            'tipo_producto': 'Producto',
            'descripcion': p.descripcion,
            'precio': str(p.precio),
            'imagen': p.imagen.url if p.imagen else '',
        })

    return JsonResponse({'arreglos': data})
