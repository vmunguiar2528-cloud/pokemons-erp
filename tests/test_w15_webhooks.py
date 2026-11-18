from decimal import Decimal
from unittest.mock import patch

import stripe
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from configuracion.models import ConfiguracionERP
from productos.models import Categoria, Producto
from ventas.models import Pedido


def crear_evento(tipo, pedido_id):
    return {
        'type': tipo,
        'data': {'object': {
            'id': f'pi_test_{pedido_id}',
            'metadata': {'pedido_id': str(pedido_id)},
            'status': 'succeeded' if 'succeeded' in tipo else 'failed',
        }},
    }


class WebhookSegurityTest(TestCase):
    def test_get_rechazado_con_405(self):
        r = self.client.get(reverse('catalogo:webhook'))
        self.assertEqual(r.status_code, 405)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_firma_invalida_devuelve_400(self, mock_construct):
        mock_construct.side_effect = stripe.error.SignatureVerificationError('Test', 'sig')
        r = self.client.post(reverse('catalogo:webhook'), data=b'{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='invalid')
        self.assertEqual(r.status_code, 400)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_payload_invalido_devuelve_400(self, mock_construct):
        mock_construct.side_effect = ValueError('JSON inválido')
        r = self.client.post(reverse('catalogo:webhook'), data=b'no-json', content_type='application/json')
        self.assertEqual(r.status_code, 400)


class WebhookPagoTest(TestCase):
    def setUp(self):
        ConfiguracionERP.get_instance()
        categoria = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(nombre='P', precio=Decimal('500'), stock=10, categoria=categoria)
        cliente = Cliente.objects.create(nombre='C', correo='c@test.com')
        self.pedido = Pedido.objects.create(
            numero_pedido='PED-2026-0001',
            cliente=cliente,
            estado='pendiente',
            total_pagado=Decimal('1160'),
            items_snapshot=[{'producto_id': self.prod.pk, 'nombre': 'P', 'cantidad': 2, 'precio': '500'}],
        )

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_succeeded_actualiza_y_descuenta_stock(self, mock_construct):
        mock_construct.return_value = crear_evento('payment_intent.succeeded', self.pedido.pk)
        r = self.client.post(reverse('catalogo:webhook'), data=b'{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='ok')
        self.assertEqual(r.status_code, 200)
        self.pedido.refresh_from_db()
        self.prod.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'pagado')
        self.assertEqual(self.prod.stock, 8)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_succeeded_es_idempotente(self, mock_construct):
        self.pedido.estado = 'pagado'
        self.pedido.save()
        stock_antes = self.prod.stock
        mock_construct.return_value = crear_evento('payment_intent.succeeded', self.pedido.pk)
        self.client.post(reverse('catalogo:webhook'), data=b'{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='ok')
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.stock, stock_antes)

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_failed_cancela_pedido(self, mock_construct):
        mock_construct.return_value = crear_evento('payment_intent.payment_failed', self.pedido.pk)
        r = self.client.post(reverse('catalogo:webhook'), data=b'{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='ok')
        self.assertEqual(r.status_code, 200)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'cancelado')

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_sin_pedido_id_retorna_200(self, mock_construct):
        evento = crear_evento('payment_intent.succeeded', self.pedido.pk)
        evento['data']['object']['metadata'] = {}
        mock_construct.return_value = evento
        r = self.client.post(reverse('catalogo:webhook'), data=b'{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='ok')
        self.assertEqual(r.status_code, 200)


class WebhookStripeObjectTest(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(nombre='P', precio=Decimal('500'), stock=10, categoria=categoria)
        cliente = Cliente.objects.create(nombre='C', correo='c2@test.com')
        self.pedido = Pedido.objects.create(numero_pedido='PED-2026-0002', cliente=cliente, estado='pendiente', total_pagado=Decimal('1160'), items_snapshot=[{'producto_id': self.prod.pk, 'cantidad': 2}])

    @patch('catalogo.webhook_views.stripe.Webhook.construct_event')
    def test_evento_stripe_object_real(self, mock_construct):
        datos = crear_evento('payment_intent.succeeded', self.pedido.pk)
        datos.update({'id': 'evt_test', 'object': 'event'})
        datos['data']['object']['object'] = 'payment_intent'
        mock_construct.return_value = stripe.Event.construct_from(datos, 'sk_test')
        r = self.client.post(reverse('catalogo:webhook'), data=b'{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='ok')
        self.assertEqual(r.status_code, 200)
        self.pedido.refresh_from_db()
        self.prod.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'pagado')
        self.assertEqual(self.prod.stock, 8)
