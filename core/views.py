from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from catalogo.models import Producto
from usuarios.decorators import panel_login_required

from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'core/index.html')


def PanelAdmin_base(request):
    return render(request, 'core/panel_admin_base.html')


@panel_login_required
def dashboard_view(request):
    """
    Vista principal del panel de administración.
    Requiere autenticación y permisos de staff.
    """
    User = get_user_model()
    # Estadísticas generales
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    usuarios_staff = User.objects.filter(is_staff=True).count()
    mes_actual = timezone.now().month
    nuevos_usuarios_mes = User.objects.filter(
        date_joined__month=mes_actual
    ).count()

    # Últimos usuarios registrados
    ultimos_usuarios = User.objects.order_by('-date_joined')[:5]

    context = {
        'titulo': 'Panel de Administración',
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_staff': usuarios_staff,
        'nuevos_usuarios_mes': nuevos_usuarios_mes,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'core/dashboard.html', context)


# Nuevas vistas de páginas públicas

def nosotros(request):
    return render(request, 'core/nosotros.html')


def productos(request):
    return render(request, 'core/productos.html')


def contactanos(request):
    return render(request, 'core/contactanos.html')


def productos(request):
    # Traemos todos los productos guardados
    productos_db = Producto.objects.all() 
    return render(request, 'catalogo.html', {'productos': productos_db})


from django.shortcuts import render

def error_404(request, exception):
    if request.path.startswith("/admin"):
        return render(request, "core/404_admin.html", status=404)
    return render(request, "core/404_index.html", status=404)






