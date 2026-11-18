from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from clientes.models import Cliente
from configuracion.models import ConfiguracionERP
from productos.models import Categoria, Producto
from ventas.models import Pedido


@override_settings(
    STRIPE_SECRET_KEY='sk_test_testkey',
    STRIPE_PUBLISHABLE_KEY='pk_test_testkey',
)
class CheckoutTest(TestCase):
    def setUp(self):
        ConfiguracionERP.get_instance()
        categoria = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(nombre='Laptop', precio=Decimal('500'), stock=5, categoria=categoria)
        self.user = User.objects.create_user('payer', password='pass', email='payer@test.com')
        self.client.force_login(self.user)
        self.client.post(reverse('catalogo:agregar', args=[self.prod.pk]), {'cantidad': 2})

    def test_checkout_sin_auth_redirige_login(self):
        self.client.logout()
        r = self.client.get(reverse('catalogo:checkout'))
        self.assertEqual(r.status_code, 302)

    def test_checkout_get_con_carrito(self):
        r = self.client.get(reverse('catalogo:checkout'))
        self.assertEqual(r.status_code, 200)

    @patch('catalogo.views.stripe.PaymentIntent.create')
    def test_post_crea_pedido_y_cliente(self, mock_pi):
        mock_pi.return_value = MagicMock(client_secret='pi_test_secret')
        r = self.client.post(reverse('catalogo:checkout'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.estado, 'pendiente')
        self.assertTrue(Cliente.objects.filter(correo='payer@test.com').exists())

    @patch('catalogo.views.stripe.PaymentIntent.create')
    def test_post_crea_snapshot(self, mock_pi):
        mock_pi.return_value = MagicMock(client_secret='pi_test_secret')
        self.client.post(reverse('catalogo:checkout'))
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.items_snapshot[0]['producto_id'], self.prod.pk)
        self.assertEqual(pedido.items_snapshot[0]['cantidad'], 2)

    @patch('catalogo.views.stripe.PaymentIntent.create')
    def test_stripe_recibe_monto_en_centavos(self, mock_pi):
        mock_pi.return_value = MagicMock(client_secret='pi_test_secret')
        self.client.post(reverse('catalogo:checkout'))
        config = ConfiguracionERP.get_instance()
        total = Decimal('1000') + Decimal('1000') * (config.iva_porcentaje / 100)
        kwargs = mock_pi.call_args.kwargs
        self.assertEqual(kwargs['amount'], int(total * 100))

    @patch('catalogo.views.stripe.PaymentIntent.create')
    def test_post_checkout_calcula_iva(self, mock_pi):
        mock_pi.return_value = MagicMock(client_secret='pi_test_secret')
        self.client.post(reverse('catalogo:checkout'))
        pedido = Pedido.objects.first()
        config = ConfiguracionERP.get_instance()
        subtotal = Decimal('1000.00')
        esperado = subtotal + subtotal * (config.iva_porcentaje / 100)
        self.assertEqual(pedido.total_pagado, esperado)


class PagoExitosoTest(TestCase):
    def test_pago_exitoso_vacia_carrito(self):
        cliente = Cliente.objects.create(nombre='C', correo='c@test.com')
        pedido = Pedido.objects.create(numero_pedido='PED-2026-0099', cliente=cliente, estado='pendiente', total_pagado=Decimal('116'))
        session = self.client.session
        session['carrito'] = {'1': {'nombre': 'P', 'precio': '100', 'cantidad': 1}}
        session.save()
        r = self.client.get(reverse('catalogo:pago_exitoso', args=[pedido.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.session.get('carrito', {}), {})

    def test_pago_exitoso_devuelve_200(self):
        cliente = Cliente.objects.create(nombre='C', correo='c2@test.com')
        pedido = Pedido.objects.create(numero_pedido='PED-2026-0098', cliente=cliente, estado='pendiente', total_pagado=Decimal('116'))
        r = self.client.get(reverse('catalogo:pago_exitoso', args=[pedido.pk]))
        self.assertEqual(r.status_code, 200)
