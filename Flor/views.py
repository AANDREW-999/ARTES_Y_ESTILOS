from django.shortcuts import render
from usuarios.decorators import panel_login_required


@panel_login_required
def lista_flor(request):
	return render(request, 'flor/lista.html')

# Create your views here.
