from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views import generic

from datetime import date, datetime

from flor.models import Flor
from producto.models import Producto
from proveedores.models import Proveedor

from .forms import CompraForm
from .models import Compra, DetalleCompra


def _parse_item_id(raw_item_id):
    tipo_raw, raw_id = (raw_item_id or "").split("-", 1)
    item_id = int(raw_id)
    if tipo_raw == "F":
        return "FLOR", item_id
    if tipo_raw == "P":
        return "PRODUCTO", item_id
    raise ValueError("Tipo de item invalido")


def _parse_detalles_compra(request):
    item_ids = request.POST.getlist("item_id[]")
    precios = request.POST.getlist("precio[]")
    cantidades = request.POST.getlist("cantidad[]")

    detalles = []
    for idx, (item_id_raw, precio_raw, cantidad_raw) in enumerate(zip(item_ids, precios, cantidades), start=1):
        item_id_raw = str(item_id_raw).strip()
        precio_raw = str(precio_raw).strip()
        cantidad_raw = str(cantidad_raw).strip()

        if not item_id_raw and not precio_raw and not cantidad_raw:
            continue

        if not item_id_raw:
            raise ValueError(f"Articulo {idx}: Debe seleccionar un item.")
        if not precio_raw or not cantidad_raw:
            raise ValueError(f"Articulo {idx}: Debe completar precio y cantidad.")

        try:
            tipo_item, item_pk = _parse_item_id(item_id_raw)
        except (ValueError, TypeError):
            raise ValueError(f"Articulo {idx}: Item invalido.")

        try:
            precio_normalizado = precio_raw
            if "," in precio_raw:
                precio_normalizado = precio_raw.replace(".", "").replace(",", ".")

            precio_limpio = Decimal(precio_normalizado)
            cantidad_limpia = int(cantidad_raw)
        except (InvalidOperation, ValueError):
            raise ValueError(f"Articulo {idx}: Formato invalido en precio o cantidad.")

        if precio_limpio <= 0:
            raise ValueError(f"Articulo {idx}: El precio debe ser mayor a 0.")
        if cantidad_limpia <= 0:
            raise ValueError(f"Articulo {idx}: La cantidad debe ser mayor a 0.")

        detalles.append(
            {
                "tipo_item": tipo_item,
                "item_pk": item_pk,
                "cantidad": cantidad_limpia,
                "precio": precio_limpio,
            }
        )

    if not detalles:
        raise ValueError("Debe agregar al menos un articulo con precio y cantidad validos.")

    return detalles


def _bloquear_item(tipo_item, item_pk):
    if tipo_item == "FLOR":
        return Flor.objects.select_for_update().get(pk=item_pk)
    return Producto.objects.select_for_update().get(pk=item_pk)


def _sumar_stock_item(tipo_item, item_pk, cantidad):
    item = _bloquear_item(tipo_item, item_pk)
    item.cantidad += cantidad
    item.save(update_fields=["cantidad"])


def _restar_stock_item(tipo_item, item_pk, cantidad, contexto):
    item = _bloquear_item(tipo_item, item_pk)
    if item.cantidad < cantidad:
        raise ValueError(
            f"No hay stock suficiente para ajustar {item.nombre} en {contexto}. Disponible: {item.cantidad}, requerido: {cantidad}."
        )
    item.cantidad -= cantidad
    item.save(update_fields=["cantidad"])


def compras_list(request):
    lista_compras = Compra.objects.select_related("proveedor", "usuario").prefetch_related(
        "detalles__flor", "detalles__producto"
    )

    q = request.GET.get("q", "").strip()
    proveedor_nombre = request.GET.get("proveedor_nombre", "").strip()
    fecha_desde = request.GET.get("fecha_desde", "")

    if q:
        filtros_q = (
            Q(descripcion__icontains=q) |
            Q(proveedor__nombre_proveedor__icontains=q) |
            Q(proveedor__numero_documento__icontains=q)
        )
        if q.isdigit():
            filtros_q = filtros_q | Q(id=int(q))
        lista_compras = lista_compras.filter(filtros_q)

    if proveedor_nombre:
        lista_compras = lista_compras.filter(proveedor__nombre_proveedor__icontains=proveedor_nombre)

    if fecha_desde:
        try:
            fecha = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            lista_compras = lista_compras.filter(fecha_emision__gte=fecha)
        except ValueError:
            fecha_desde = ""

    template = loader.get_template("lista_compra.html")
    proveedores = Proveedor.objects.all().order_by("nombre_proveedor")

    total_compras = lista_compras.count()
    monto_total = lista_compras.aggregate(Sum("total_compra"))["total_compra__sum"] or 0
    total_proveedores = lista_compras.values("proveedor").distinct().count()

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    compras_mes = lista_compras.filter(fecha_emision__gte=inicio_mes, fecha_emision__lte=hoy).count()

    context = {
        "compras": lista_compras,
        "query": q,
        "total_compras": total_compras,
        "monto_total": monto_total,
        "total_proveedores": total_proveedores,
        "compras_mes": compras_mes,
        "proveedores": proveedores,
        "proveedor_nombre_filtro": proveedor_nombre,
        "fecha_desde_filtro": fecha_desde,
        "resultados_filtrados": lista_compras.count(),
        "hay_filtros": any([q, proveedor_nombre, fecha_desde]),
    }
    return HttpResponse(template.render(context, request))


def compra_detail(request, id):
    una_compra = get_object_or_404(
        Compra.objects.select_related("proveedor", "usuario").prefetch_related("detalles__flor", "detalles__producto"),
        id=id,
    )
    template = loader.get_template("compra_detail.html")

    context = {
        "compra": una_compra,
        "detalles": una_compra.detalles.all(),
    }
    return HttpResponse(template.render(context, request))


class CompraCreateView(LoginRequiredMixin, generic.CreateView):
    model = Compra
    form_class = CompraForm
    template_name = "crear_compra.html"
    success_url = reverse_lazy("compras:lista_compra")
    login_url = "usuarios:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proveedores"] = Proveedor.objects.filter(activo=True).order_by("nombre_proveedor")
        context["flores"] = Flor.objects.all().order_by("nombre")
        context["productos"] = Producto.objects.all().order_by("nombre")
        return context

    def form_valid(self, form):
        try:
            detalles = _parse_detalles_compra(self.request)
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                compra = form.save(commit=False)
                compra.subtotal = 0
                compra.total_compra = 0
                compra.usuario = self.request.user
                compra.save()

                for data in detalles:
                    detalle = DetalleCompra(
                        compra=compra,
                        tipo_item=data["tipo_item"],
                        cantidad=data["cantidad"],
                        precio=data["precio"],
                    )
                    if data["tipo_item"] == "FLOR":
                        detalle.flor = Flor.objects.get(pk=data["item_pk"])
                    else:
                        detalle.producto = Producto.objects.get(pk=data["item_pk"])
                    detalle.save()

                    _sumar_stock_item(data["tipo_item"], data["item_pk"], data["cantidad"])

                compra.calcular_totales()

            messages.success(self.request, f"Compra registrada exitosamente con {len(detalles)} item(s).")
            return redirect(self.success_url)
        except (Flor.DoesNotExist, Producto.DoesNotExist):
            messages.error(self.request, "Uno de los items seleccionados ya no existe.")
            return self.form_invalid(form)
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
        except Exception as exc:
            messages.error(self.request, f"Error al guardar la compra: {exc}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor, corrija los errores en el formulario.")
        return super().form_invalid(form)


class CompraUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Compra
    form_class = CompraForm
    template_name = "editar_compra.html"
    success_url = reverse_lazy("compras:lista_compra")
    pk_url_kwarg = "compra_id"
    login_url = "usuarios:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proveedores"] = Proveedor.objects.filter(activo=True).order_by("nombre_proveedor")
        context["detalles"] = self.object.detalles.select_related("flor", "producto")
        context["flores"] = Flor.objects.all().order_by("nombre")
        context["productos"] = Producto.objects.all().order_by("nombre")
        return context

    def form_valid(self, form):
        try:
            nuevos_detalles = _parse_detalles_compra(self.request)
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

        compra = self.get_object()

        try:
            with transaction.atomic():
                compra = form.save()

                detalles_actuales = list(compra.detalles.select_related("flor", "producto"))

                for detalle in detalles_actuales:
                    item_pk = detalle.flor_id if detalle.tipo_item == "FLOR" else detalle.producto_id
                    if not item_pk:
                        continue

                    _restar_stock_item(
                        detalle.tipo_item,
                        item_pk,
                        detalle.cantidad,
                        "la edicion de compra",
                    )

                compra.detalles.all().delete()

                for data in nuevos_detalles:
                    detalle = DetalleCompra(
                        compra=compra,
                        tipo_item=data["tipo_item"],
                        cantidad=data["cantidad"],
                        precio=data["precio"],
                    )
                    if data["tipo_item"] == "FLOR":
                        detalle.flor = Flor.objects.get(pk=data["item_pk"])
                    else:
                        detalle.producto = Producto.objects.get(pk=data["item_pk"])
                    detalle.save()

                    _sumar_stock_item(data["tipo_item"], data["item_pk"], data["cantidad"])

                compra.calcular_totales()

            messages.success(self.request, f"Compra actualizada exitosamente con {len(nuevos_detalles)} item(s).")
            return redirect(self.success_url)
        except (Flor.DoesNotExist, Producto.DoesNotExist):
            messages.error(self.request, "Uno de los items seleccionados ya no existe.")
            return self.form_invalid(form)
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
        except Exception as exc:
            messages.error(self.request, f"Error al actualizar la compra: {exc}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor, corrija los errores en el formulario.")
        return super().form_invalid(form)


class CompraDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Compra
    template_name = "eliminar_compra.html"
    success_url = reverse_lazy("compras:lista_compra")
    pk_url_kwarg = "compra_id"
    login_url = "usuarios:login"

    def post(self, request, *args, **kwargs):
        compra = self.get_object()
        try:
            with transaction.atomic():
                detalles = list(compra.detalles.select_related("flor", "producto"))
                for detalle in detalles:
                    item_pk = detalle.flor_id if detalle.tipo_item == "FLOR" else detalle.producto_id
                    if not item_pk:
                        continue

                    _restar_stock_item(
                        detalle.tipo_item,
                        item_pk,
                        detalle.cantidad,
                        "la eliminacion de compra",
                    )
                compra.delete()

            messages.success(request, f"La compra {compra.id} ha sido eliminada exitosamente.")
        except ValueError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            messages.error(request, f"No se pudo eliminar la compra: {exc}")

        return redirect(self.success_url)
