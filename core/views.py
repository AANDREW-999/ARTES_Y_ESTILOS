from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from catalogo.models import Producto
from usuarios.decorators import panel_login_required
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from .forms import ContactoForm
from django.template.loader import render_to_string

# Create your views here.

def index(request):
    busqueda = request.GET.get('busqueda', '')

    if busqueda:
        productos = Producto.objects.filter(nombre__icontains=busqueda)
    else:
        productos = Producto.objects.all()

    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']

            subject = f"Nuevo mensaje de {nombre}"
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)
            recipient_list = ["arteyestilos.test@gmail.com"]
            context = {
                "nombre": nombre,
                "email": email,
                "mensaje": mensaje,
            }
            body_text = render_to_string("core/email_contacto.txt", context)
            body_html = render_to_string("core/email_contacto.html", context)

            email_message = EmailMultiAlternatives(
                subject=subject,
                body=body_text,
                from_email=from_email,
                to=recipient_list,
                reply_to=[email],
            )
            email_message.attach_alternative(body_html, "text/html")
            email_message.send(fail_silently=False)

            messages.success(request, "Tu mensaje fue enviado correctamente 💌")
            return redirect('core:landing')
    else:
        form = ContactoForm()

    context = {
        'productos': productos,
        'busqueda': busqueda,
        'form': form
    }

    return render(request, 'core/index.html', context)


def PanelAdmin_base(request):
    return render(request, 'panel_admin_base.html')


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
    return render(request, 'admin/dashboard.html', context)


# Nuevas vistas de páginas públicas


def error_404(request, exception):
    if request.path.startswith("/admin"):
        return render(request, "admin/404_admin.html", status=404)
    return render(request, "core/404_index.html", status=404)






