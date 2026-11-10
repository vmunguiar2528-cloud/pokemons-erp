from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.home, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path(
        'exportar/excel/',
        views.exportar_excel_productos,
        name='exportar_excel',
    ),
    path('exportar/pdf/', views.exportar_pdf_ventas, name='exportar_pdf'),
]