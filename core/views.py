from django.shortcuts import render

def bienvenida(request):
    modulos = [
        {'nombre': 'Productos', 'icono': '📦', 'url': '/productos/', 'descripcion': 'Inventario y catálogo'},
        {'nombre': 'Clientes', 'icono': '👥', 'url': '/clientes/', 'descripcion': 'Cartera de clientes'},
        {'nombre': 'Proveedores', 'icono': '🏭', 'url': '/proveedores/', 'descripcion': 'Red de proveedores'},
        {'nombre': 'Ventas', 'icono': '💰', 'url': '/ventas/', 'descripcion': 'Pedidos y facturación'},
        {'nombre': 'Reportes', 'icono': '📊', 'url': '/reportes/', 'descripcion': 'Dashboard y analítica'},
        {'nombre': 'Admin', 'icono': '⚙️', 'url': '/admin/', 'descripcion': 'Panel de administración'},
    ]
    return render(request, 'bienvenida.html', {'modulos': modulos})