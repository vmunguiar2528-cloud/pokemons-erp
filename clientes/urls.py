from django.urls import path

from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.lista_clientes, name='lista'),
    path('<int:pk>/', views.detalle_cliente, name='detalle'),
    path('nuevo/', views.crear_cliente, name='crear'),
    path('editar/<int:pk>/', views.editar_cliente, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar'),
]