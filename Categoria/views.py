from django.shortcuts import render
from usuarios.decorators import panel_login_required


@panel_login_required
def lista_categoria(request):
	return render(request, 'categoria/lista.html')

# Create your views here.
