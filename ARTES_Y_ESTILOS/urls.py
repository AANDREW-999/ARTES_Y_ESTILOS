"""
URL configuration for ARTES_Y_ESTILOS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

handler404 = 'core.views.error_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('usuarios.urls')),
    path('', include('catalogo.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('compras/', include('compras.urls')),  
    path('clientes/', include('clientes.urls')), 
    path('ventas/', include('ventas.urls')),
    path('arreglo', include('arreglo.urls')),
    # Ruta específica para el favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/FaviconAE.png', permanent=True)),
]

if settings.DEBUG:
    # Servir archivos estáticos en desarrollo
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Servir archivos media (uploads de usuarios)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
