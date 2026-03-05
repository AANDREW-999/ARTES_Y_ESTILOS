from django.urls import path
from . import views

app_name = 'flor'

urlpatterns = [
    path('', views.lista_flor, name='lista'),
]
