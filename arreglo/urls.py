from django.urls import path
from . import views

app_name = 'arreglo'

urlpatterns = [

    path('gestion/', views.gestion_arreglo, name='gestion'),
    path('agregar/', views.agregar_arreglo, name='agregar'),
    path('detalle/<int:id>/', views.detalle_arreglo, name='detalle'),
    path('editar/<int:id>/', views.editar_arreglo, name='editar'),
    path('eliminar/<int:id>/', views.eliminar_arreglo, name='eliminar'),
]