import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.files.base import ContentFile
from .models import Producto


def _procesar_imagen(request, nombre_producto):
    """
    Retorna el archivo de imagen a guardar:
    - Si viene cropped_image_data (Base64 del cropper) → lo decodifica y retorna ContentFile
    - Si viene imagen normal (FILES) → la retorna directamente
    - Si no viene nada → retorna None
    """
    cropped_data = request.POST.get('cropped_image_data', '').strip()

    if cropped_data:
        try:
            # Formato: "data:image/jpeg;base64,/9j/4AAQ..."
            encabezado, imgstr = cropped_data.split(';base64,')
            ext = encabezado.split('/')[-1]  # jpeg, png, etc.
            nombre_archivo = f"producto_{nombre_producto}.{ext}"
            return ContentFile(base64.b64decode(imgstr), name=nombre_archivo)
        except Exception:
            pass  # Si falla el decode, intenta con FILES

    return request.FILES.get('imagen') or None


# 1. LISTAR (con búsqueda por nombre, categoría y descripción)
def lista_productos(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__icontains=query)
        ).order_by('-id')
    else:
        productos = Producto.objects.all().order_by('-id')
    return render(request, 'catalogo_producto.html', {
        'productos': productos,
        'busqueda': query
    })


# 2. AGREGAR
def agregar_producto(request):
    if request.method == 'POST':
        nombre    = request.POST.get('nombre')
        precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '.')

        imagen = _procesar_imagen(request, nombre)

        Producto.objects.create(
            nombre=nombre,
            categoria=request.POST.get('categoria'),
            precio=precio_raw,
            tamano=request.POST.get('tamano'),
            descripcion=request.POST.get('descripcion'),
            imagen=imagen
        )
        return redirect('catalogo:gestion_productos')

    return render(request, 'agregar_catalogo_producto.html', {
        'categorias_list': Producto.CATEGORIAS
    })


# 3. EDITAR
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '.')

        producto.nombre     = nombre
        producto.categoria  = request.POST.get('categoria')
        producto.precio     = precio_raw
        producto.tamano     = request.POST.get('tamano')
        producto.descripcion = request.POST.get('descripcion')

        imagen = _procesar_imagen(request, nombre)
        if imagen:
            producto.imagen = imagen

        producto.save()
        return redirect('catalogo:gestion_productos')

    return render(request, 'editar_catalogo_producto.html', {
        'producto': producto,
        'categorias_list': Producto.CATEGORIAS
    })


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