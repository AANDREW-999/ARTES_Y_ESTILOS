from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.ClienteListView.as_view(), name='lista_clientes'),
    path('crear/', views.ClienteCreateView.as_view(), name='crear_cliente'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='detalle_cliente'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='editar_cliente'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='eliminar_cliente'),
    path('verificar-documento/', views.verificar_documento, name='verificar_documento'),
]