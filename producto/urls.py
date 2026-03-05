from django.urls import path
from . import views

app_name = 'producto'

urlpatterns = [
    path('', views.lista_producto, name='lista'),
]
