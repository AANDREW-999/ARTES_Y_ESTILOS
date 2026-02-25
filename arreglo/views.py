from django.shortcuts import render, redirect, get_object_or_404
from .models import Arreglo
from .forms import ArregloForm

# 1. LISTAR: Solo muestra la tabla o tarjetas
def gestion_arreglo(request):
    # Traemos todos los arreglos, los más nuevos primero
    arreglos = Arreglo.objects.all().order_by('-id')
    return render(request, 'gestion_arreglo.html', {'arreglos': arreglos})

# 2. AGREGAR: Página independiente para crear
def agregar_arreglo(request):
    if request.method == 'POST':
        form = ArregloForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('arreglo:gestion')
    else:
        form = ArregloForm()
    
    # CAMBIO: Usamos el nombre corto que acordamos
    return render(request, 'agregar_arreglo.html', {'form': form})

# 3. DETALLE: Información completa
def detalle_arreglo(request, id):
    arreglo = get_object_or_404(Arreglo, id=id)
    return render(request, 'detalle_arreglo.html', {'arreglo': arreglo})

# 4. EDITAR: Modificar datos existentes
def editar_arreglo(request, id):
    arreglo = get_object_or_404(Arreglo, id=id)
    if request.method == 'POST':
        form = ArregloForm(request.POST, request.FILES, instance=arreglo)
        if form.is_valid():
            form.save()
            return redirect('arreglo:gestion')
    else:
        form = ArregloForm(instance=arreglo)
    return render(request, 'editar_arreglo.html', {'form': form, 'arreglo': arreglo})

# 5. ELIMINAR: Borrado físico
def eliminar_arreglo(request, id):
    arreglo = get_object_or_404(Arreglo, id=id)
    if request.method == 'POST':
        arreglo.delete()
    return redirect('arreglo:gestion')