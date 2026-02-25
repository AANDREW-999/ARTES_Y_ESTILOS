from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    
    path('gestion/', views.lista_productos, name='gestion_productos'), 
    path('agregar/', views.agregar_producto, name='agregar_producto'), 
    path('detalle/<int:pk>/', views.detalle_producto, name='detalle_producto'), 
    path('editar/<int:id>/', views.editar_producto, name='editar_producto'), 
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
]