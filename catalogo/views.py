from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto

# 1. LISTAR PRODUCTOS 
def lista_productos(request):
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        productos = Producto.objects.filter(nombre__icontains=busqueda) #
    else:
        productos = Producto.objects.all() #
    
   
    return render(request, 'catalogo_producto.html', {
        'productos': productos,
        'busqueda': busqueda,
    }) #

# 2. AGREGAR PRODUCTO (Corregido)
def agregar_producto(request):

    if request.method == 'POST':
        precio_raw = request.POST.get('precio', '0')
        precio_limpio = precio_raw.replace(',', '.') 

        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            categoria=request.POST.get('categoria'),
            precio=precio_limpio,
            tamano=request.POST.get('tamano'),
            descripcion=request.POST.get('descripcion'),
            imagen=request.FILES.get('imagen')
        )
        
        return redirect('catalogo:gestion_productos')

    
    return render(request, 'agregar_catalogo_producto.html', {
        'categorias_list': Producto.CATEGORIAS
    })

# 3. EDITAR PRODUCTO 
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id) 
    
    if request.method == 'POST':
        precio_raw = request.POST.get('precio', '0')
        producto.precio = precio_raw.replace(',', '.') 
        producto.nombre = request.POST.get('nombre')
        producto.categoria = request.POST.get('categoria')
        producto.tamano = request.POST.get('tamano')
        producto.descripcion = request.POST.get('descripcion')
        
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen') 
            
        producto.save() 
        return redirect('catalogo:gestion_productos') 

   
    return render(request, 'editar_catalogo_producto.html', {
        'producto': producto,
        'categorias_list': Producto.CATEGORIAS
    }) #

# 4. ELIMINAR PRODUCTO 
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id) 
    if request.method == 'POST':
        producto.delete() 
    return redirect('catalogo:gestion_productos') 

# 5. DETALLE DE PRODUCTO 
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk) 
    return render(request, 'detalle_catalogo_producto.html', {
        'producto': producto
    }) 