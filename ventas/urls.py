from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('listar',           views.listar_ventas,  name='listar_venta'),
    path('crear/',           views.crear_venta,    name='crear'),
    path('<int:pk>/',        views.detalle_venta,  name='detalle'),
    path('<int:pk>/editar/', views.editar_venta,   name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_venta, name='eliminar'),
    path('ajax/clientes/',   views.buscar_cliente, name='buscar_cliente'),
    path('ajax/arreglos/',   views.buscar_arreglo, name='buscar_arreglo'),
]