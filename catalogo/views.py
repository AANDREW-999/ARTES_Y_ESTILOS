from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto

# 1. LISTAR PRODUCTOS (Tu tabla de gestión)
def lista_productos(request):
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        productos = Producto.objects.filter(nombre__icontains=busqueda)
    else:
        productos = Producto.objects.all()

    categorias_list = Producto.CATEGORIAS 
    
    # IMPORTANTE: Cambiado a SINGULAR para que coincida con tu archivo image_c90b84.png
    return render(request, 'catalogo_producto.html', {
        'productos': productos,
        'categorias_list': categorias_list,
        'busqueda': busqueda 
    })

# 2. AGREGAR PRODUCTO
def agregar_producto(request):
    if request.method == 'POST':
        precio_raw = request.POST.get('precio', '0')
        precio_limpio = precio_raw.replace(',', '.')

        nombre = request.POST.get('nombre')
        categoria = request.POST.get('categoria')
        tamano = request.POST.get('tamano')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen') 

        Producto.objects.create(
            nombre=nombre,
            categoria=categoria,
            precio=precio_limpio,
            tamano=tamano,
            descripcion=descripcion,
            imagen=imagen
        )

    return redirect('catalogo:gestion_productos')

# 3. EDITAR PRODUCTO
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        precio_raw = request.POST.get('precio', '0')
        precio_limpio = precio_raw.replace(',', '.')

        producto.nombre = request.POST.get('nombre')
        producto.categoria = request.POST.get('categoria')
        producto.precio = precio_limpio
        producto.tamano = request.POST.get('tamano')
        producto.descripcion = request.POST.get('descripcion')
        
        nueva_imagen = request.FILES.get('imagen')
        if nueva_imagen:
            producto.imagen = nueva_imagen
            
        producto.save() 
      
        return redirect('catalogo:gestion_productos')

    # Usamos el nombre exacto de tu archivo: editar_catalogo_producto.html
    return render(request, 'editar_catalogo_producto.html', {
        'producto': producto,
        'categorias_list': Producto.CATEGORIAS
    })

# 4. ELIMINAR PRODUCTO
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('catalogo:gestion_productos')

# 5. DETALLE DE PRODUCTO
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    # Usamos el nombre exacto de tu archivo: detalle_catalogo_producto.html
    return render(request, 'detalle_catalogo_producto.html', {
        'producto': producto
    })