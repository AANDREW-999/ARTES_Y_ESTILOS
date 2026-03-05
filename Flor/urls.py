from django.urls import path
from . import views

app_name = 'flor'

urlpatterns = [
    path('', views.FlorListView.as_view(), name='lista'),
    path('crear/', views.FlorCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', views.FlorUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.FlorDeleteView.as_view(), name='eliminar'),
]
