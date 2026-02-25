from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Venta
from .forms import VentaForm
from clientes.models import Cliente
#from arreglos.models import Arreglo


def listar_ventas(request):
    ventas = Venta.objects.select_related('cliente' )
    return render(request, 'ventas/listar_venta.html', {'ventas': ventas})


def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            form.save()
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
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})


def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == 'POST':
        venta.delete()
        return redirect('ventas:listar')

    return render(request, 'ventas/eliminar_venta.html', {'venta': venta})


def buscar_cliente(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.filter(nombre__icontains=q)
    data = list(clientes.values(
        'id', 'nombre', 'direccion'
    ))
    return JsonResponse({'clientes': data})


#def buscar_arreglo(request):
    q = request.GET.get('q', '')
    arreglos = Arreglo.objects.filter(nombre__icontains=q)
    data = list(arreglos.values(
        'id', 'nombre', 'precio'
    ))
    return JsonResponse({'arreglos': data})
