import logging

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from productos.models import Producto
from ventas.models import Pedido

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request) -> HttpResponse:
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        logger.warning('Webhook: payload inválido recibido.')
        return HttpResponse('Payload inválido.', status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning('Webhook: firma inválida — posible ataque.')
        return HttpResponse('Firma inválida.', status=400)

    if hasattr(event, 'to_dict'):
        event = event.to_dict()

    tipo = event['type']
    logger.info(f'Webhook recibido: {tipo}')

    if tipo == 'payment_intent.succeeded':
        _manejar_pago_exitoso(event['data']['object'])
    elif tipo == 'payment_intent.payment_failed':
        _manejar_pago_fallido(event['data']['object'])
    else:
        logger.debug(f'Evento ignorado: {tipo}')

    return HttpResponse(status=200)


def _manejar_pago_exitoso(payment_intent: dict) -> None:
    pedido_id = _extraer_pedido_id(payment_intent)
    if pedido_id is None:
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Webhook: Pedido {pedido_id} no encontrado en BD.')
        return

    if pedido.estado != Pedido.Estado.PAGADO:
        pedido.estado = Pedido.Estado.PAGADO
        pedido.save(update_fields=['estado'])
        logger.info(f'Pedido {pedido.numero_pedido} actualizado a "pagado".')
        _descontar_stock(pedido)
        _enviar_confirmacion_compra(pedido)
        _enviar_sms_confirmacion(pedido)
    else:
        logger.info(
            f'Pedido {pedido.numero_pedido} ya estaba pagado — '
            'idempotente, sin cambios.'
        )


def _manejar_pago_fallido(payment_intent: dict) -> None:
    pedido_id = _extraer_pedido_id(payment_intent)
    if pedido_id is None:
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Webhook: Pedido {pedido_id} no encontrado.')
        return

    if pedido.estado == Pedido.Estado.PENDIENTE:
        pedido.estado = Pedido.Estado.CANCELADO
        pedido.save(update_fields=['estado'])
        logger.info(f'Pedido {pedido.numero_pedido} cancelado por pago fallido.')


def _extraer_pedido_id(payment_intent: dict) -> int | None:
    metadata = payment_intent.get('metadata', {})
    pedido_id = metadata.get('pedido_id')
    if not pedido_id:
        logger.warning(
            'Webhook: PaymentIntent sin pedido_id en metadata. '
            f'ID: {payment_intent.get("id")}'
        )
        return None

    try:
        return int(pedido_id)
    except (ValueError, TypeError):
        logger.error(f'Webhook: pedido_id inválido: {pedido_id!r}')
        return None


def _descontar_stock(pedido: Pedido) -> None:
    for item in pedido.items_snapshot or []:
        producto_id = item.get('producto_id')
        cantidad = int(item.get('cantidad', 0))
        if not producto_id or cantidad <= 0:
            continue

        filas_actualizadas = Producto.objects.filter(
            pk=producto_id,
            stock__gte=cantidad,
        ).update(stock=F('stock') - cantidad)

        if filas_actualizadas:
            logger.info(
                f'Stock decrementado: Producto {producto_id} - '
                f'{cantidad} unidades.'
            )
        else:
            logger.warning(
                f'Producto {producto_id}: stock insuficiente para '
                f'decrementar {cantidad} unidades.'
            )


def _enviar_confirmacion_compra(pedido: Pedido) -> None:
    cliente = pedido.cliente
    lineas = [
        f"- {item.get('nombre', 'Producto')} x {item.get('cantidad', 0)} — ${item.get('precio', '0')}"
        for item in (pedido.items_snapshot or [])
    ]
    detalle = '\n'.join(lineas) or '- Compra realizada'

    mensaje = (
        f"Hola {cliente.nombre},\n\n"
        f"Confirmamos que tu compra fue exitosa.\n"
        f"Pedido: {pedido.numero_pedido}\n"
        f"Total pagado: ${pedido.total_pagado}\n\n"
        f"Productos:\n{detalle}\n\n"
        "Gracias por tu compra."
    )

    destinatarios = [cliente.correo]

    purchase_email = getattr(
        settings,
        'PURCHASE_NOTIFICATION_EMAIL',
        'v.munguiar.2528@cbtis198.edu.mx',
    ).strip()
    if purchase_email and purchase_email not in destinatarios:
        destinatarios.append(purchase_email)

    if getattr(settings, 'SALES_EMAIL', ''):
        sales_email = settings.SALES_EMAIL.strip()
        if sales_email and sales_email not in destinatarios:
            destinatarios.append(sales_email)

    try:
        send_mail(
            subject=f'Compra confirmada - {pedido.numero_pedido}',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False,
        )
        logger.info('Correo de confirmación enviado para %s', pedido.numero_pedido)
    except Exception as exc:
        logger.exception(
            'No se pudo enviar el correo del pedido %s: %s',
            pedido.numero_pedido,
            exc,
        )


def _enviar_sms_confirmacion(pedido: Pedido) -> None:
    mensaje = (
        f"Compra confirmada. Pedido {pedido.numero_pedido}. "
        f"Total: ${pedido.total_pagado}. Gracias por tu compra."
    )

    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    remitente = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
    destino = getattr(settings, 'SMS_DESTINATION_NUMBER', '+5246110557584')

    if not sid or not token or not remitente:
        logger.warning(
            'SMS no enviado: faltan TWILIO_ACCOUNT_SID, '
            'TWILIO_AUTH_TOKEN o TWILIO_PHONE_NUMBER. Mensaje: %s',
            mensaje,
        )
        return

    try:
        from twilio.rest import Client

        client = Client(sid, token)
        sms = client.messages.create(
            body=mensaje,
            from_=remitente,
            to=destino,
        )
        logger.info('SMS enviado al número configurado. SID: %s', sms.sid)
    except Exception as exc:
        logger.exception('No se pudo enviar el SMS del pedido %s: %s', pedido.numero_pedido, exc)
