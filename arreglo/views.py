from django.shortcuts import render, redirect, get_object_or_404
from .models import Arreglo
from .forms import ArregloForm

# Gestión: Lista los arreglos y permite agregar uno nuevo desde un Modal
def gestion_arreglo(request):
    arreglos = Arreglo.objects.all()
    if request.method == 'POST':
        form = ArregloForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('arreglo:gestion')
    else:
        form = ArregloForm()
    return render(request, 'gestion_arreglo.html', {'arreglos': arreglos, 'form': form})

# Detalle: Muestra la información completa de un solo arreglo
def detalle_arreglo(request, id):
    arreglo = get_object_or_404(Arreglo, id=id)
    return render(request, 'detalle_arreglo.html', {'arreglo': arreglo})

# Editar: Formulario para modificar un arreglo existente
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

# Eliminar: Borra el registro de la base de datos
def eliminar_arreglo(request, id):
    arreglo = get_object_or_404(Arreglo, id=id)
    if request.method == 'POST':
        arreglo.delete()
    return redirect('arreglo:gestion')

# Create your views here.
