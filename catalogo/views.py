from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q 
from .models import Producto

# 1. LISTAR (Con búsqueda q)
def lista_productos(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query)).order_by('-id')
    else:
        productos = Producto.objects.all().order_by('-id')
    return render(request, 'catalogo_producto.html', {'productos': productos, 'busqueda': query})

# 2. AGREGAR
def agregar_producto(request):
    if request.method == 'POST':
        precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '.')
        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            categoria=request.POST.get('categoria'),
            precio=precio_raw,
            tamano=request.POST.get('tamano'),
            descripcion=request.POST.get('descripcion'),
            imagen=request.FILES.get('imagen')
        )
        return redirect('catalogo:gestion_productos')
    return render(request, 'agregar_catalogo_producto.html', {'categorias_list': Producto.CATEGORIAS})

# 3. EDITAR
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '.')
        producto.precio = precio_raw
        producto.nombre = request.POST.get('nombre')
        producto.categoria = request.POST.get('categoria')
        producto.tamano = request.POST.get('tamano')
        producto.descripcion = request.POST.get('descripcion')
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen')
        producto.save()
        return redirect('catalogo:gestion_productos')
    return render(request, 'editar_catalogo_producto.html', {'producto': producto, 'categorias_list': Producto.CATEGORIAS})

# 4. ELIMINAR
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
    return redirect('catalogo:gestion_productos')

# 5. DETALLE
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'detalle_catalogo_producto.html', {'producto': producto})