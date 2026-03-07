import base64
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.core.files.base import ContentFile
from django.contrib import messages
from .models import Producto

from categoria.models import Categoria


def _parse_decimal(valor):
    """Convierte un string de filtro a Decimal, tolerando formato con miles."""
    if valor is None:
        return None

    limpio = str(valor).strip()
    if not limpio:
        return None

    normalizado = limpio.replace('.', '').replace(',', '.')
    try:
        return Decimal(normalizado)
    except (InvalidOperation, ValueError):
        return None


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
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    estado = request.GET.get('estado', '').strip()
    tamano = request.GET.get('tamano', '').strip()
    precio_min_raw = request.GET.get('precio_min', '').strip()
    precio_max_raw = request.GET.get('precio_max', '').strip()

    productos = Producto.objects.select_related('categoria').all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(tamano__icontains=query)
        )

    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))

    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)

    if tamano:
        productos = productos.filter(tamano__iexact=tamano)

    precio_min = _parse_decimal(precio_min_raw)
    precio_max = _parse_decimal(precio_max_raw)

    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        precio_min, precio_max = precio_max, precio_min
        precio_min_raw = str(precio_min)
        precio_max_raw = str(precio_max)
        messages.info(request, 'Se ajusto el rango de precios porque el minimo era mayor al maximo.')

    if precio_min is not None:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max is not None:
        productos = productos.filter(precio__lte=precio_max)

    productos = productos.order_by('-id')

    total_productos = Producto.objects.count()
    total_activos = Producto.objects.filter(activo=True).count()
    total_inactivos = total_productos - total_activos
    total_categorias = Producto.objects.values('categoria_id').distinct().count()

    return render(request, 'catalogo_producto.html', {
        'productos': productos,
        'busqueda': query,
        'categorias_filtro': Categoria.objects.filter(activo=True).order_by('nombre'),
        'tamanos_filtro': Producto.objects.exclude(tamano__isnull=True).exclude(tamano='').values_list('tamano', flat=True).distinct().order_by('tamano'),
        'categoria_filtro': categoria_id,
        'estado_filtro': estado,
        'tamano_filtro': tamano,
        'precio_min_filtro': precio_min_raw,
        'precio_max_filtro': precio_max_raw,
        'total_productos': total_productos,
        'total_activos': total_activos,
        'total_inactivos': total_inactivos,
        'total_categorias': total_categorias,
        'resultados_filtrados': productos.count(),
        'hay_filtros': any([query, categoria_id, estado, tamano, precio_min_raw, precio_max_raw]),
    })


# 2. AGREGAR
def agregar_producto(request):
    if request.method == 'POST':
        try:
            nombre    = request.POST.get('nombre')
            precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '.')
            activo = request.POST.get('activo') == 'on'

            categoria_id = request.POST.get('categoria')
            categoria = Categoria.objects.filter(pk=categoria_id).first()
            if not categoria:
                messages.error(request, 'Debes seleccionar una categoría válida.')
                return redirect('catalogo:agregar_producto')

            imagen = _procesar_imagen(request, nombre)

            Producto.objects.create(
                nombre=nombre,
                categoria=categoria,
                precio=precio_raw,
                tamano=request.POST.get('tamano'),
                descripcion=request.POST.get('descripcion'),
                activo=activo,
                imagen=imagen
            )
            messages.success(request, 'Producto creado correctamente.')
            return redirect('catalogo:gestion_productos')
        except Exception:
            messages.error(request, 'No se pudo crear el producto. Verifica los datos e inténtalo nuevamente.')
            return redirect('catalogo:gestion_productos')

    return render(request, 'agregar_catalogo_producto.html', {
        'categorias_list': Categoria.objects.all().order_by('nombre')
    })


# 3. EDITAR
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '.')

            categoria_id = request.POST.get('categoria')
            categoria = Categoria.objects.filter(pk=categoria_id).first()
            if not categoria:
                messages.error(request, 'Debes seleccionar una categoría válida.')
                return redirect('catalogo:editar_producto', id=producto.id)

            producto.nombre     = nombre
            producto.categoria  = categoria
            producto.precio     = precio_raw
            producto.tamano     = request.POST.get('tamano')
            producto.descripcion = request.POST.get('descripcion')
            producto.activo = request.POST.get('activo') == 'on'

            imagen = _procesar_imagen(request, nombre)
            if imagen:
                producto.imagen = imagen

            producto.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('catalogo:gestion_productos')
        except Exception:
            messages.error(request, 'No se pudo actualizar el producto. Verifica los datos e inténtalo nuevamente.')
            return redirect('catalogo:gestion_productos')

    return render(request, 'editar_catalogo_producto.html', {
        'producto': producto,
        'categorias_list': Categoria.objects.all().order_by('nombre')
    })


# 4. ELIMINAR
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        try:
            producto.delete()
            messages.success(request, 'Producto eliminado correctamente.')
        except Exception:
            messages.error(request, 'No se pudo eliminar el producto. Inténtalo nuevamente.')
        return redirect('catalogo:gestion_productos')

    return render(request, 'eliminar_catalogo_producto.html', {
        'producto': producto,
    })


# 5. DETALLE
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'detalle_catalogo_producto.html', {'producto': producto})