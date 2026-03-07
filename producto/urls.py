from django.urls import path
from . import views

app_name = 'producto'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='lista'),
    path('crear/', views.ProductoCreateView.as_view(), name='crear'),
    path('detalle/<int:pk>/', views.ProductoDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='eliminar'),
]
