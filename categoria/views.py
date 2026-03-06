import base64

from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from usuarios.decorators import panel_login_required

from .forms import CategoriaForm
from .models import Categoria


def _procesar_imagen(request, nombre_categoria: str):
	"""Procesa imagen enviada por cropper (Base64) o por FILES."""
	cropped_data = request.POST.get('cropped_image_data', '').strip()

	if cropped_data:
		try:
			encabezado, imgstr = cropped_data.split(';base64,')
			ext = encabezado.split('/')[-1]
			nombre_archivo = f"categoria_{nombre_categoria}.{ext}"
			return ContentFile(base64.b64decode(imgstr), name=nombre_archivo)
		except Exception:
			pass

	return request.FILES.get('imagen') or None


@panel_login_required
def lista_categoria(request):
	categorias = Categoria.objects.all().order_by('nombre')
	return render(request, 'categoria/lista.html', {
		'categorias': categorias,
	})


@panel_login_required
def agregar_categoria(request):
	if request.method == 'POST':
		form = CategoriaForm(request.POST)
		if form.is_valid():
			categoria = form.save(commit=False)
			imagen = _procesar_imagen(request, categoria.nombre)
			if imagen:
				categoria.imagen = imagen
			categoria.save()
			messages.success(request, 'Categoría creada correctamente.')
			return redirect('categoria:lista')
		messages.error(request, 'Por favor, revisa los campos del formulario.')
	else:
		form = CategoriaForm()

	return render(request, 'categoria/form.html', {
		'form': form,
		'modo': 'crear',
	})


@panel_login_required
def editar_categoria(request, pk: int):
	categoria = get_object_or_404(Categoria, pk=pk)

	if request.method == 'POST':
		form = CategoriaForm(request.POST, instance=categoria)
		if form.is_valid():
			categoria = form.save(commit=False)
			imagen = _procesar_imagen(request, categoria.nombre)
			if imagen:
				categoria.imagen = imagen
			categoria.save()
			messages.success(request, 'Categoría actualizada correctamente.')
			return redirect('categoria:lista')
		messages.error(request, 'Por favor, revisa los campos del formulario.')
	else:
		form = CategoriaForm(instance=categoria)

	return render(request, 'categoria/form.html', {
		'form': form,
		'categoria': categoria,
		'modo': 'editar',
	})


@panel_login_required
def eliminar_categoria(request, pk: int):
	categoria = get_object_or_404(Categoria, pk=pk)

	if request.method == 'POST':
		nombre = categoria.nombre
		try:
			categoria.delete()
			messages.success(request, f'Categoría "{nombre}" eliminada correctamente.')
		except Exception:
			messages.error(request, 'No se pudo eliminar la categoría. Verifica si está en uso por productos.')
		return redirect('categoria:lista')

	return render(request, 'categoria/eliminar.html', {
		'categoria': categoria,
	})

