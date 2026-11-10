from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.lista_ventas, name='lista'),
    path('nuevo/', views.crear_venta, name='crear'),
]