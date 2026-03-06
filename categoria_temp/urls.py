from django.urls import path
from . import views

app_name = 'categoria'

urlpatterns = [
    path('', views.lista_categoria, name='lista'),
]
