from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.listar_proveedores, name='listar'),
    path('agregar/', views.agregar_proveedor, name='agregar'),
    path('editar/<int:pk>/', views.editar_proveedor, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar'),
    path('detalle/<int:pk>/', views.detalle_proveedor, name='detalle'),
]
