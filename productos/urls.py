from django.urls import path

from . import api, views

app_name = 'productos'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('<int:pk>/', views.detalle_producto, name='detalle'),
    path('nuevo/', views.crear_producto, name='crear'),
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
    path('api/', api.ProductoListCreateAPIView.as_view(), name='api_list_create'),
    path('api/<int:pk>/', api.ProductoDetailAPIView.as_view(), name='api_detail'),
]