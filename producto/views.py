from django.shortcuts import render
from usuarios.decorators import panel_login_required


@panel_login_required
def lista_producto(request):
	return render(request, 'producto/lista.html')

# Create your views here.
