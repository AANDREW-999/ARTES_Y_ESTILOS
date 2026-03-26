import base64
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.core.files.base import ContentFile
from django.contrib import messages
from .models import Producto
from core.notifications import crear_notificacion
from usuarios.decorators import panel_login_required

from categoria.models import Categoria
from io import BytesIO
from PIL import Image
from core.sanitize import validar_y_sanitizar


# Extensiones y tipos MIME permitidos para imágenes
EXTENSIONES_PERMITIDAS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
TIPOS_MIME_PERMITIDOS = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'
}


def _es_imagen_valida(archivo):
    """
    Valida que el archivo sea realmente una imagen.
    Retorna True si es válida, False en caso contrario.
    """
    try:
        # Obtener la extensión
        nombre_archivo = archivo.name.lower()
        _, ext = nombre_archivo.rsplit('.', 1) if '.' in nombre_archivo else ('', '')
        
        # Validar extensión
        if ext not in EXTENSIONES_PERMITIDAS:
            return False
        
        # Validar tipo MIME si está disponible
        mime_type = getattr(archivo, 'content_type', '').lower()
        if mime_type and mime_type not in TIPOS_MIME_PERMITIDOS:
            return False
        
        # Validar que sea realmente una imagen usando PIL
        try:
            archivo.seek(0)  # Reiniciar al inicio
            img = Image.open(archivo)
            img.verify()  # Verificar que sea una imagen válida
            return True
        except Exception:
            return False
    except Exception:
        return False


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
    - Si viene imagen normal (FILES) → valida y retorna
    - Si no viene nada o es inválida → retorna None
    """
    cropped_data = request.POST.get('cropped_image_data', '').strip()

    if cropped_data:
        try:
            # Formato: "data:image/jpeg;base64,/9j/4AAQ..."
            encabezado, imgstr = cropped_data.split(';base64,')
            mime_type = encabezado.split(':')[1] if ':' in encabezado else ''
            
            # Validar tipo MIME del base64
            if mime_type.lower() not in TIPOS_MIME_PERMITIDOS:
                return None
            
            ext = mime_type.split('/')[-1]  # jpeg, png, etc.
            
            # Validar extensión
            if ext not in EXTENSIONES_PERMITIDAS:
                return None
            
            # Decodificar y validar que sea una imagen real
            datos_imagen = base64.b64decode(imgstr)
            
            # Validar usando PIL
            try:
                img = Image.open(BytesIO(datos_imagen))
                img.verify()
            except Exception:
                return None
            
            nombre_archivo = f"producto_{nombre_producto}.{ext}"
            return ContentFile(datos_imagen, name=nombre_archivo)
        except Exception:
            return None  # Si falla, no retorna imagen

    # Validar archivo tradicional
    archivo = request.FILES.get('imagen')
    if archivo and _es_imagen_valida(archivo):
        return archivo
    
    return None


# 1. LISTAR (con búsqueda por nombre, categoría y descripción)
@login_required
@panel_login_required
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
@login_required
@panel_login_required
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

            # Validar imagen
            archivo_imagen = request.FILES.get('imagen')
            cropped_data = request.POST.get('cropped_image_data', '').strip()
            
            if archivo_imagen and not _es_imagen_valida(archivo_imagen):
                messages.error(request, 'Por favor, carga solo archivos de imagen (JPG, PNG, GIF, WEBP o BMP).')
                return redirect('catalogo:agregar_producto')
            
            if cropped_data:
                try:
                    encabezado = cropped_data.split(';base64,')[0]
                    mime_type = encabezado.split(':')[1] if ':' in encabezado else ''
                    if mime_type.lower() not in TIPOS_MIME_PERMITIDOS:
                        messages.error(request, 'Por favor, carga solo archivos de imagen (JPG, PNG, GIF, WEBP o BMP).')
                        return redirect('catalogo:agregar_producto')
                except:
                    pass

            imagen = _procesar_imagen(request, nombre)
            
            if (archivo_imagen or cropped_data) and not imagen:
                messages.error(request, 'El archivo de imagen no es válido. Por favor, verifica que sea una imagen real.')
                return redirect('catalogo:agregar_producto')

            # Sanitizar descripción para prevenir XSS
            descripcion = validar_y_sanitizar('Descripción', request.POST.get('descripcion', ''))

            Producto.objects.create(
                nombre=nombre,
                categoria=categoria,
                precio=precio_raw,
                tamano=request.POST.get('tamano'),
                descripcion=descripcion,
                activo=activo,
                imagen=imagen
            )
            crear_notificacion(
                categoria='movimiento',
                estilo='success',
                titulo='Producto de catalogo creado',
                mensaje=f'Se creo el producto {nombre}.',
            )
            messages.success(request, 'Producto creado correctamente.')
            return redirect('catalogo:gestion_productos')
        except Exception as e:
            messages.error(request, 'No se pudo crear el producto. Verifica los datos e inténtalo nuevamente.')
            return redirect('catalogo:gestion_productos')

    return render(request, 'agregar_catalogo_producto.html', {
        'categorias_list': Categoria.objects.all().order_by('nombre')
    })


# 3. EDITAR
@login_required
@panel_login_required
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

            # Validar imagen
            archivo_imagen = request.FILES.get('imagen')
            cropped_data = request.POST.get('cropped_image_data', '').strip()
            
            if archivo_imagen and not _es_imagen_valida(archivo_imagen):
                messages.error(request, 'Por favor, carga solo archivos de imagen (JPG, PNG, GIF, WEBP o BMP).')
                return redirect('catalogo:editar_producto', id=producto.id)
            
            if cropped_data:
                try:
                    encabezado = cropped_data.split(';base64,')[0]
                    mime_type = encabezado.split(':')[1] if ':' in encabezado else ''
                    if mime_type.lower() not in TIPOS_MIME_PERMITIDOS:
                        messages.error(request, 'Por favor, carga solo archivos de imagen (JPG, PNG, GIF, WEBP o BMP).')
                        return redirect('catalogo:editar_producto', id=producto.id)
                except:
                    pass

            producto.nombre     = nombre
            producto.categoria  = categoria
            producto.precio     = precio_raw
            producto.tamano     = request.POST.get('tamano')
            
            # Sanitizar descripción para prevenir XSS
            descripcion = validar_y_sanitizar('Descripción', request.POST.get('descripcion', ''))
            producto.descripcion = descripcion
            
            producto.activo = request.POST.get('activo') == 'on'

            imagen = _procesar_imagen(request, nombre)
            
            if (archivo_imagen or cropped_data) and not imagen:
                messages.error(request, 'El archivo de imagen no es válido. Por favor, verifica que sea una imagen real.')
                return redirect('catalogo:editar_producto', id=producto.id)
            
            if imagen:
                producto.imagen = imagen

            producto.save()
            crear_notificacion(
                categoria='movimiento',
                estilo='info',
                titulo='Producto de catalogo actualizado',
                mensaje=f'Se actualizo el producto {producto.nombre}.',
            )
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('catalogo:gestion_productos')
        except Exception as e:
            messages.error(request, 'No se pudo actualizar el producto. Verifica los datos e inténtalo nuevamente.')
            return redirect('catalogo:gestion_productos')

    return render(request, 'editar_catalogo_producto.html', {
        'producto': producto,
        'categorias_list': Categoria.objects.all().order_by('nombre')
    })


# 4. ELIMINAR
@login_required
@panel_login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        try:
            nombre = producto.nombre
            crear_notificacion(
                categoria='movimiento',
                estilo='error',
                titulo='Producto de catalogo eliminado',
                mensaje=f'Se elimino el producto {nombre}.',
            )
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