from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import Venta, DetalleVenta
from .forms import VentaForm
from clientes.models import Cliente
from arreglo.models import Arreglo


def listar_ventas(request):
    ventas = Venta.objects.select_related('cliente').prefetch_related('detalles__arreglo')
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
            messages.error(request, 'Debes agregar al menos un arreglo a la venta.')
        elif form.is_valid():
            venta = form.save(commit=False)
            venta.total = Decimal('0')
            venta.save()

            for aid, cant, prec in items_validos:
                try:
                    DetalleVenta.objects.create(
                        venta      = venta,
                        arreglo_id = int(aid),
                        cantidad   = int(cant),
                        precio     = Decimal(prec),
                    )
                except (ValueError, Exception):
                    pass

            venta.recalcular_totales()
            venta.save(update_fields=['subtotal_sin_iva', 'iva_monto', 'total'])

            messages.success(request, f'Venta #{venta.id} registrada correctamente.')
            return redirect('ventas:listar')

    else:
        form = VentaForm()

    return render(request, 'ventas/agregar_venta.html', {'form': form})


def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            return redirect('ventas:listar')
    else:
        form = VentaForm(instance=venta)

    return render(request, 'ventas/editar_venta.html', {'form': form, 'venta': venta})


def detalle_venta(request, pk):
    venta = get_object_or_404(
        Venta.objects.prefetch_related('detalles__arreglo').select_related('cliente'),
        pk=pk
    )
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})


def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == 'POST':
        venta.delete()
        return redirect('ventas:listar')

    return render(request, 'ventas/eliminar_venta.html', {'venta': venta})


def buscar_cliente(request):
    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.filter(nombre__icontains=q)[:10]
    data = list(clientes.values('id', 'nombre', 'direccion'))
    return JsonResponse({'clientes': data})

def buscar_arreglo(request):
    q = request.GET.get('q', '').strip()

    qs = Arreglo.objects.filter(
        nombre_flor__icontains=q
    )[:10]

    data = [
        {
            'nombre_flor': a.nombre_flor,
            'tipo_producto': a.tipo_producto,
            'descripcion': a.descripcion,
            'precio': str(a.precio),              
            'imagen': a.imagen.url if a.imagen else '',
        }
        for a in qs
    ]

    return JsonResponse({'arreglos': data})
