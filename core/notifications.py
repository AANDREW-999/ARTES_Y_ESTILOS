from .models import Notificacion


MAX_NOTIFICACIONES_GUARDADAS = 200


def _depurar_historial_notificaciones():
    ids_a_borrar = list(
        Notificacion.objects.order_by("-creada_en").values_list("id", flat=True)[MAX_NOTIFICACIONES_GUARDADAS:]
    )
    if ids_a_borrar:
        Notificacion.objects.filter(id__in=ids_a_borrar).delete()


def crear_notificacion(categoria, estilo, titulo, mensaje, nivel_stock=""):
    Notificacion.objects.create(
        categoria=categoria,
        estilo=estilo,
        titulo=titulo,
        mensaje=mensaje,
        nivel_stock=nivel_stock,
    )
    _depurar_historial_notificaciones()


def obtener_nivel_stock(cantidad):
    if cantidad <= 0:
        return "agotado"
    if cantidad <= 10:
        return "bajo"
    if cantidad <= 30:
        return "medio"
    return "alto"


def crear_notificacion_stock(nombre_item, cantidad, origen=""):
    nivel = obtener_nivel_stock(cantidad)

    if nivel == "agotado":
        estilo = "error"
        titulo = "Stock agotado"
        mensaje = f"No quedan unidades de {nombre_item}."
    elif nivel == "bajo":
        estilo = "warning"
        titulo = "Stock bajo"
        mensaje = f"Quedan {cantidad} unidades de {nombre_item}."
    elif nivel == "medio":
        estilo = "info"
        titulo = "Stock medio"
        mensaje = f"Quedan {cantidad} unidades de {nombre_item}."
    else:
        estilo = "success"
        titulo = "Stock alto"
        mensaje = f"Quedan {cantidad} unidades de {nombre_item}."

    if origen:
        mensaje = f"{mensaje} ({origen})"

    crear_notificacion(
        categoria="stock",
        estilo=estilo,
        titulo=titulo,
        mensaje=mensaje,
        nivel_stock=nivel,
    )
