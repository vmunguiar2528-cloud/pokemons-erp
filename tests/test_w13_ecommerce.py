from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from productos.models import Categoria, Producto


class CatalogoCarritoTest(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nombre='Electrónica')
        self.prod1 = Producto.objects.create(nombre='Laptop', precio=Decimal('10000'), stock=5, categoria=categoria)
        self.prod2 = Producto.objects.create(nombre='Mouse', precio=Decimal('250'), stock=20, categoria=categoria)

    def test_catalogo_sin_auth(self):
        r = self.client.get(reverse('catalogo:catalogo'))
        self.assertEqual(r.status_code, 200)

    def test_filtro_nombre(self):
        r = self.client.get(reverse('catalogo:catalogo'), {'nombre': 'lapt'})
        nombres = [p.nombre for p in r.context['productos']]
        self.assertIn('Laptop', nombres)
        self.assertNotIn('Mouse', nombres)

    def test_agregar_acumula(self):
        url = reverse('catalogo:agregar', args=[self.prod1.pk])
        self.client.post(url, {'cantidad': 1})
        self.client.post(url, {'cantidad': 3})
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.context['items'][0]['cantidad'], 4)

    def test_total_correcto(self):
        self.client.post(reverse('catalogo:agregar', args=[self.prod2.pk]), {'cantidad': 2})
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.context['total'], Decimal('500.00'))

    def test_remover(self):
        url = reverse('catalogo:agregar', args=[self.prod1.pk])
        self.client.post(url, {'cantidad': 1})
        self.client.post(reverse('catalogo:remover', args=[self.prod1.pk]))
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.context['items'], [])

    def test_producto_inactivo_no_aparece(self):
        Producto.objects.create(nombre='Inactivo', precio=Decimal('100'), stock=5, activo=False, categoria=self.prod1.categoria)
        r = self.client.get(reverse('catalogo:catalogo'))
        nombres = [p.nombre for p in r.context['productos']]
        self.assertNotIn('Inactivo', nombres)

    def test_filtro_precio_maximo(self):
        r = self.client.get(reverse('catalogo:catalogo'), {'precio_max': 500})
        nombres = [p.nombre for p in r.context['productos']]
        self.assertIn('Mouse', nombres)
        self.assertNotIn('Laptop', nombres)

    def test_actualizar_cero_elimina_producto(self):
        agregar = reverse('catalogo:agregar', args=[self.prod1.pk])
        self.client.post(agregar, {'cantidad': 1})
        self.client.post(reverse('catalogo:actualizar', args=[self.prod1.pk]), {'cantidad': 0})
        r = self.client.get(reverse('catalogo:carrito'))
        self.assertEqual(r.context['items'], [])
