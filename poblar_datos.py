import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from clientes.models import Cliente
from proveedores.models import Proveedor
from productos.models import Categoria, Producto
from ventas.models import Venta

def poblar():
    print('Cargando datos de prueba...')
    
    # Proveedores
    p1, _ = Proveedor.objects.get_or_create(nombre='TecnoSuministros', empresa='TecnoSuministros S.A.', correo='contacto@tecnosuministros.com', telefono='5551234567')
    p2, _ = Proveedor.objects.get_or_create(nombre='Distribuidora Global', empresa='Global Logistics', correo='ventas@globallogistics.com', telefono='5559876543')

    # Categorías
    cat1, _ = Categoria.objects.get_or_create(nombre='Electrónica', descripcion='Equipos y accesorios')
    cat2, _ = Categoria.objects.get_or_create(nombre='Oficina', descripcion='Insumos de oficina')

    # Productos
    prod1, _ = Producto.objects.get_or_create(nombre='Laptop Exec', categoria=cat1, proveedor=p1, precio=15000.00, stock=10)
    prod2, _ = Producto.objects.get_or_create(nombre='Mouse Inalámbrico', categoria=cat1, proveedor=p1, precio=350.00, stock=50)
    prod3, _ = Producto.objects.get_or_create(nombre='Silla Ergonómica', categoria=cat2, proveedor=p2, precio=3200.00, stock=15)

    # Clientes
    c1, _ = Cliente.objects.get_or_create(nombre='Juan Pérez', correo='juan.perez@gmail.com', telefono='5551112233')
    c2, _ = Cliente.objects.get_or_create(nombre='María López', correo='maria.lopez@hotmail.com', telefono='5554445566')

    # Ventas
    Venta.objects.get_or_create(cliente=c1, total=15350.00)
    Venta.objects.get_or_create(cliente=c2, total=3200.00)

    print('¡Datos de prueba cargados exitosamente!')

if __name__ == '__main__':
    poblar()
