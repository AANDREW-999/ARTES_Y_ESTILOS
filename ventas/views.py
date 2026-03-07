from decimal import Decimal, InvalidOperation
from datetime import date, datetime

from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from clientes.models import Cliente
from flor.models import Flor
from producto.models import Producto

from .forms import VentaForm
from .models import DetalleVenta, Venta


def _parse_item_id(raw_item_id):
    tipo_raw, raw_id = (raw_item_id or "").split("-", 1)
    item_id = int(raw_id)
    if tipo_raw == "F":
        return "FLOR", item_id
    if tipo_raw == "P":
        return "PRODUCTO", item_id
    raise ValueError("Tipo de item invalido")


def _parse_detalles_venta(request):
    arreglo_ids = request.POST.getlist("arreglo_id[]")
    cantidades = request.POST.getlist("cantidad[]")
    precios = request.POST.getlist("precio[]")

    detalles = []
    for idx, (arreglo_id, cantidad_raw, precio_raw) in enumerate(zip(arreglo_ids, cantidades, precios), start=1):
        arreglo_id = str(arreglo_id).strip()
        cantidad_raw = str(cantidad_raw).strip()
        precio_raw = str(precio_raw).strip()

        if not arreglo_id and not cantidad_raw and not precio_raw:
            continue

        if not arreglo_id:
            raise ValueError(f"Item {idx}: Debes seleccionar un flor o producto.")

        try:
            tipo_item, item_pk = _parse_item_id(arreglo_id)
        except (ValueError, TypeError):
            raise ValueError(f"Item {idx}: Identificador invalido.")

        try:
            cantidad = int(cantidad_raw)
        except ValueError:
            raise ValueError(f"Item {idx}: Formato invalido en cantidad.")

        precio = None
        if precio_raw:
            try:
                precio = Decimal(precio_raw)
            except InvalidOperation:
                raise ValueError(f"Item {idx}: Formato invalido en precio.")

        if not precio or precio <= 0:
            # Fallback: si no llega precio en el POST, tomar el precio actual del item.
            try:
                if tipo_item == "FLOR":
                    precio = Flor.objects.get(pk=item_pk).precio
                else:
                    precio = Producto.objects.get(pk=item_pk).precio
            except (Flor.DoesNotExist, Producto.DoesNotExist):
                raise ValueError(f"Item {idx}: El item seleccionado ya no existe.")

        if cantidad <= 0:
            raise ValueError(f"Item {idx}: La cantidad debe ser mayor a 0.")
        if precio <= 0:
            raise ValueError(f"Item {idx}: El precio debe ser mayor a 0.")

        detalles.append(
            {
                "tipo_item": tipo_item,
                "item_pk": item_pk,
                "cantidad": cantidad,
                "precio": precio,
            }
        )

    if not detalles:
        raise ValueError("Debes agregar al menos un item a la venta.")

    return detalles


def _lock_item(tipo_item, item_pk):
    if tipo_item == "FLOR":
        return Flor.objects.select_for_update().get(pk=item_pk)
    return Producto.objects.select_for_update().get(pk=item_pk)


def _descontar_stock(tipo_item, item_pk, cantidad):
    item = _lock_item(tipo_item, item_pk)
    if item.cantidad < cantidad:
        raise ValueError(
            f"Stock insuficiente para {item.nombre}. Disponible: {item.cantidad}, solicitado: {cantidad}."
        )
    item.cantidad -= cantidad
    item.save(update_fields=["cantidad"])


def _devolver_stock(tipo_item, item_pk, cantidad):
    item = _lock_item(tipo_item, item_pk)
    item.cantidad += cantidad
    item.save(update_fields=["cantidad"])


def listar_ventas(request):
    ventas = Venta.objects.select_related("cliente").prefetch_related("detalles__flor", "detalles__producto")

    q = request.GET.get("q", "").strip()
    cliente_nombre = request.GET.get("cliente_nombre", "").strip()
    fecha_desde = request.GET.get("fecha_desde", "").strip()

    def _parse_fecha(raw_fecha):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(raw_fecha, fmt).date()
            except ValueError:
                continue
        return None

    if q:
        filtros_q = (
            Q(cliente__nombre__icontains=q) |
            Q(cliente__apellido__icontains=q) |
            Q(cliente__documento__icontains=q)
        )
        if q.isdigit():
            filtros_q = filtros_q | Q(id=int(q))
        ventas = ventas.filter(filtros_q)

    if cliente_nombre:
        partes_nombre = [p for p in cliente_nombre.split() if p]
        filtro_cliente = Q(cliente__nombre__icontains=cliente_nombre) | Q(cliente__apellido__icontains=cliente_nombre)

        if len(partes_nombre) >= 2:
            primer_token = partes_nombre[0]
            resto_nombre = " ".join(partes_nombre[1:])
            filtro_cliente = filtro_cliente | (
                Q(cliente__nombre__icontains=primer_token) & Q(cliente__apellido__icontains=resto_nombre)
            ) | (
                Q(cliente__apellido__icontains=primer_token) & Q(cliente__nombre__icontains=resto_nombre)
            )

        ventas = ventas.filter(filtro_cliente)

    if fecha_desde:
        fecha = _parse_fecha(fecha_desde)
        if fecha:
            ventas = ventas.filter(fecha__gte=fecha)
        else:
            fecha_desde = ""

    clientes = Cliente.objects.all().order_by("nombre", "apellido")

    total_ventas = ventas.count()
    monto_total = ventas.aggregate(Sum("total"))["total__sum"] or 0
    total_clientes = ventas.values("cliente").distinct().count()

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    ventas_mes = ventas.filter(fecha__gte=inicio_mes, fecha__lte=hoy).count()

    context = {
        "ventas": ventas,
        "query": q,
        "clientes": clientes,
        "cliente_nombre_filtro": cliente_nombre,
        "fecha_desde_filtro": fecha_desde,
        "total_ventas": total_ventas,
        "monto_total": monto_total,
        "total_clientes": total_clientes,
        "ventas_mes": ventas_mes,
        "resultados_filtrados": ventas.count(),
        "hay_filtros": any([q, cliente_nombre, fecha_desde]),
    }
    return render(request, "ventas/listar_venta.html", context)


def crear_venta(request):
    flores = Flor.objects.all().order_by("nombre")
    productos = Producto.objects.all().order_by("nombre")

    if request.method == "POST":
        form = VentaForm(request.POST)

        try:
            detalles = _parse_detalles_venta(request)
        except ValueError as exc:
            messages.error(request, str(exc))
            return render(
                request,
                "ventas/agregar_venta.html",
                {"form": form, "flores": flores, "productos": productos},
            )

        if form.is_valid():
            try:
                with transaction.atomic():
                    venta = form.save(commit=False)
                    venta.total = Decimal("0")
                    venta.save()

                    for data in detalles:
                        detalle = DetalleVenta(
                            venta=venta,
                            tipo_item=data["tipo_item"],
                            cantidad=data["cantidad"],
                            precio=data["precio"],
                        )
                        if data["tipo_item"] == "FLOR":
                            detalle.flor = Flor.objects.get(pk=data["item_pk"])
                        else:
                            detalle.producto = Producto.objects.get(pk=data["item_pk"])
                        detalle.save()

                        _descontar_stock(data["tipo_item"], data["item_pk"], data["cantidad"])

                    venta.recalcular_totales()
                    venta.save(update_fields=["subtotal", "total"])

                messages.success(request, f"Venta #{venta.id} registrada correctamente.")
                return redirect("ventas:listar_venta")
            except (Flor.DoesNotExist, Producto.DoesNotExist):
                messages.error(request, "Uno de los items seleccionados ya no existe.")
            except ValueError as exc:
                messages.error(request, str(exc))
            except Exception as exc:
                messages.error(request, f"No se pudo registrar la venta: {exc}")
    else:
        form = VentaForm()

    return render(
        request,
        "ventas/agregar_venta.html",
        {"form": form, "flores": flores, "productos": productos},
    )


def editar_venta(request, pk):
    venta = get_object_or_404(Venta.objects.prefetch_related("detalles__flor", "detalles__producto"), pk=pk)
    flores = Flor.objects.all().order_by("nombre")
    productos = Producto.objects.all().order_by("nombre")

    if request.method == "POST":
        form = VentaForm(request.POST, instance=venta)

        try:
            nuevos_detalles = _parse_detalles_venta(request)
        except ValueError as exc:
            messages.error(request, str(exc))
            return render(
                request,
                "ventas/editar_venta.html",
                {
                    "form": form,
                    "venta": venta,
                    "detalles": venta.detalles.all(),
                    "flores": flores,
                    "productos": productos,
                },
            )

        if form.is_valid():
            try:
                with transaction.atomic():
                    venta = form.save()

                    detalles_actuales = list(venta.detalles.select_related("flor", "producto"))
                    for detalle in detalles_actuales:
                        item_pk = detalle.flor_id if detalle.tipo_item == "FLOR" else detalle.producto_id
                        if not item_pk:
                            continue

                        _devolver_stock(
                            detalle.tipo_item,
                            item_pk,
                            detalle.cantidad,
                        )

                    venta.detalles.all().delete()

                    for data in nuevos_detalles:
                        detalle = DetalleVenta(
                            venta=venta,
                            tipo_item=data["tipo_item"],
                            cantidad=data["cantidad"],
                            precio=data["precio"],
                        )
                        if data["tipo_item"] == "FLOR":
                            detalle.flor = Flor.objects.get(pk=data["item_pk"])
                        else:
                            detalle.producto = Producto.objects.get(pk=data["item_pk"])
                        detalle.save()

                        _descontar_stock(data["tipo_item"], data["item_pk"], data["cantidad"])

                    venta.recalcular_totales()
                    venta.save(update_fields=["subtotal", "total"])

                messages.success(request, f"Venta #{venta.id} actualizada correctamente.")
                return redirect("ventas:listar_venta")
            except (Flor.DoesNotExist, Producto.DoesNotExist):
                messages.error(request, "Uno de los items seleccionados ya no existe.")
            except ValueError as exc:
                messages.error(request, str(exc))
            except Exception as exc:
                messages.error(request, f"No se pudo actualizar la venta: {exc}")
    else:
        form = VentaForm(instance=venta)

    return render(
        request,
        "ventas/editar_venta.html",
        {
            "form": form,
            "venta": venta,
            "detalles": venta.detalles.all(),
            "flores": flores,
            "productos": productos,
        },
    )


def detalle_venta(request, pk):
    venta = get_object_or_404(
        Venta.objects.prefetch_related("detalles__flor", "detalles__producto").select_related("cliente"),
        pk=pk,
    )
    return render(request, "ventas/detalle_venta.html", {"venta": venta})


def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta.objects.prefetch_related("detalles__flor", "detalles__producto"), pk=pk)

    if request.method == "POST":
        try:
            with transaction.atomic():
                detalles = list(venta.detalles.select_related("flor", "producto"))
                for detalle in detalles:
                    item_pk = detalle.flor_id if detalle.tipo_item == "FLOR" else detalle.producto_id
                    if not item_pk:
                        continue

                    _devolver_stock(
                        detalle.tipo_item,
                        item_pk,
                        detalle.cantidad,
                    )
                venta.delete()

            messages.success(request, f"Venta #{pk} eliminada correctamente.")
            return redirect("ventas:listar_venta")
        except Exception as exc:
            messages.error(request, f"No se pudo eliminar la venta: {exc}")

    return render(request, "ventas/eliminar_venta.html", {"venta": venta})


def buscar_cliente(request):
    q = request.GET.get("q", "").strip()
    clientes = Cliente.objects.filter(nombre__icontains=q)[:10]
    data = list(clientes.values("id", "nombre", "direccion"))
    return JsonResponse({"clientes": data})


def buscar_arreglo(request):
    q = request.GET.get("q", "").strip()

    flores = Flor.objects.filter(nombre__icontains=q)[:10]
    productos = Producto.objects.filter(nombre__icontains=q)[:10]

    data = []
    for f in flores:
        data.append(
            {
                "id": f"F-{f.id}",
                "nombre_flor": f.nombre,
                "tipo_producto": "Flor",
                "descripcion": f.descripcion,
                "precio": str(f.precio),
                "stock": f.cantidad,
                "imagen": f.imagen.url if f.imagen else "",
            }
        )

    for p in productos:
        data.append(
            {
                "id": f"P-{p.id}",
                "nombre_flor": p.nombre,
                "tipo_producto": "Producto",
                "descripcion": p.descripcion,
                "precio": str(p.precio),
                "stock": p.cantidad,
                "imagen": p.imagen.url if p.imagen else "",
            }
        )

    return JsonResponse({"arreglos": data})
