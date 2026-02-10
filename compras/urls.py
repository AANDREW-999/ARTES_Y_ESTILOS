# urls.py (app compras)
from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.compras_list, name='lista_compras'),
    path('<int:id>/', views.compra_detail, name='compra_detail'),
    path('crear/', views.CompraCreateView.as_view(), name='crear_compra'),
    path('editar/<int:compra_id>/', views.CompraUpdateView.as_view(), name='editar_compra'),
    path('eliminar/<int:compra_id>/', views.CompraDeleteView.as_view(), name='eliminar_compra'),
]