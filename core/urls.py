from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='landing'),
    
    path('panel/dashboard/', views.dashboard_view, name='dashboard'),
    #  nuevas rutas públicas
    #  path('nosotros/', views.nosotros, name='nosotros'),
    #  path('productos/', views.productos, name='productos'),
    #  path('contactanos/', views.contactanos, name='contactanos'),
]


