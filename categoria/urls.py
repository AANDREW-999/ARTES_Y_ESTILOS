from django.urls import path
from . import views

app_name = 'categoria'

urlpatterns = [
    path('', views.lista_categoria, name='lista'),
    path('agregar/', views.agregar_categoria, name='agregar'),
    path('editar/<int:pk>/', views.editar_categoria, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar'),
]
