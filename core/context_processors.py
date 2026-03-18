from .models import Notificacion


def panel_notificaciones(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {
            "panel_notificaciones": [],
            "panel_notificaciones_no_leidas": 0,
        }

    notificaciones = list(Notificacion.objects.all()[:10])
    no_leidas = Notificacion.objects.filter(leida=False).count()

    return {
        "panel_notificaciones": notificaciones,
        "panel_notificaciones_no_leidas": no_leidas,
    }
