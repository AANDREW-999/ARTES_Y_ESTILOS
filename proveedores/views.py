from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Proveedor
from .forms import ProveedorForm

@login_required
def listar_proveedores(request):
    q = request.GET.get('q')
    proveedores = Proveedor.objects.all().order_by('-id')

    if q:
        proveedores = proveedores.filter(
            Q(nombre_proveedor__icontains=q) |
            Q(ciudad__icontains=q) |
            Q(correo_electronico__icontains=q)
        )

    context = {
        'proveedores': proveedores
    }
    return render(request, 'proveedores/listar_proveedor.html', context)

@login_required
def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado correctamente.')
            return redirect('proveedores:listar')
        messages.error(request, 'Por favor, revisa los campos del formulario.')
    else:
        form = ProveedorForm()

    context = {
        'form': form
    }
    return render(request, 'proveedores/agregar_proveedor.html', context)

@login_required
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect('proveedores:listar')
        messages.error(request, 'Por favor, revisa los campos del formulario.')
    else:
        form = ProveedorForm(instance=proveedor)

    context = {
        'form': form,
        'proveedor': proveedor
    }
    return render(request, 'proveedores/editar_proveedor.html', context)

@login_required
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        nombre = proveedor.nombre_proveedor
        proveedor.delete()
        messages.success(request, f'Proveedor "{nombre}" eliminado correctamente.')
        return redirect('proveedores:listar')

    context = {
        'proveedor': proveedor
    }
    return render(request, 'proveedores/eliminar_proveedor.html', context)

@login_required
def detalle_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    context = {
        'proveedor': proveedor
    }
    return render(request, 'proveedores/detalle_proveedor.html', context)


@login_required
def verificar_documento(request):
    """Vista AJAX para verificar si un documento de proveedor ya existe."""
    documento = request.GET.get('documento', '')
    exclude_id = request.GET.get('exclude_id', '')

    if not documento:
        return JsonResponse({'existe': False})

    queryset = Proveedor.objects.filter(numero_documento=documento)

    if exclude_id and exclude_id.isdigit():
        queryset = queryset.exclude(pk=int(exclude_id))

    return JsonResponse({'existe': queryset.exists()})
