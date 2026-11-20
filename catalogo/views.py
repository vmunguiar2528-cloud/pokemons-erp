from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from productos.models import Producto
from ventas.models import Pedido

from .checkout_utils import (
    armar_items,
    calcular_totales,
    generar_numero_pedido,
    obtener_o_crear_cliente,
)
from .filters import ProductoFilter

stripe.api_key = settings.STRIPE_SECRET_KEY


def _obtener_carrito(request):
    return request.session.get('carrito', {})


def _guardar_carrito(request, carrito):
    request.session['carrito'] = carrito
    request.session.modified = True


class CatalogoView(ListView):
    model = Producto
    template_name = 'catalogo/catalogo.html'
    context_object_name = 'productos'
    paginate_by = 12

    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True).select_related('categoria', 'proveedor').order_by('nombre')
        filtro = ProductoFilter(self.request.GET, queryset=queryset)
        return filtro.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Producto.objects.filter(activo=True).select_related('categoria', 'proveedor').order_by('nombre')
        filtro = ProductoFilter(self.request.GET, queryset=queryset)
        context['filtro'] = filtro
        return context


def ver_carrito(request):
    carrito = _obtener_carrito(request)
    items = []
    total = Decimal('0.00')

    for prod_id, datos in carrito.items():
        precio = Decimal(str(datos['precio']))
        cantidad = int(datos.get('cantidad', 1))
        subtotal = precio * cantidad
        total += subtotal
        items.append({
            'id': prod_id,
            'prod_id': prod_id,
            'nombre': datos.get('nombre', 'Producto'),
            'precio': precio,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })

    return render(request, 'catalogo/carrito.html', {
        'items': items,
        'total': total,
    })


def agregar_al_carrito(request, producto_id):
    if request.method != 'POST':
        return redirect('catalogo:catalogo')

    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    carrito = _obtener_carrito(request)
    clave = str(producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    if cantidad < 1:
        cantidad = 1

    nueva_cantidad = cantidad
    if clave in carrito:
        nueva_cantidad = int(carrito[clave]['cantidad']) + cantidad

    if nueva_cantidad > producto.stock:
        nueva_cantidad = producto.stock

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if nueva_cantidad < 1:
        messages.error(request, f'"{producto.nombre}" no tiene unidades disponibles.')
        return redirect(next_url or 'catalogo:catalogo')

    if clave in carrito:
        carrito[clave]['cantidad'] = nueva_cantidad
    else:
        carrito[clave] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': nueva_cantidad,
            'imagen': producto.imagen.name if producto.imagen else None,
        }

    _guardar_carrito(request, carrito)
    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect(next_url or 'catalogo:catalogo')


def remover_del_carrito(request, producto_id):
    if request.method != 'POST':
        return redirect('catalogo:carrito')

    carrito = _obtener_carrito(request)
    clave = str(producto_id)
    nombre = carrito.get(clave, {}).get('nombre', 'Producto')
    carrito.pop(clave, None)
    _guardar_carrito(request, carrito)
    messages.warning(request, f'"{nombre}" eliminado del carrito.')
    return redirect('catalogo:carrito')


def actualizar_cantidad(request, producto_id):
    if request.method != 'POST':
        return redirect('catalogo:carrito')

    carrito = _obtener_carrito(request)
    clave = str(producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if clave in carrito:
        if cantidad > 0:
            carrito[clave]['cantidad'] = cantidad
        else:
            carrito.pop(clave, None)

    _guardar_carrito(request, carrito)
    return redirect('catalogo:carrito')


def vaciar_carrito(request):
    if request.method == 'POST':
        _guardar_carrito(request, {})
        messages.info(request, 'Carrito vaciado.')
    return redirect('catalogo:carrito')


@login_required
def checkout(request):
    carrito = _obtener_carrito(request)
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('catalogo:catalogo')

    totales = calcular_totales(carrito)
    items = armar_items(carrito)
    publishable_key = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        clave_secreta = settings.STRIPE_SECRET_KEY
        clave_publica = settings.STRIPE_PUBLISHABLE_KEY
        claves_stripe_invalidas = (
            'placeholder' in clave_secreta
            or 'placeholder' in clave_publica
            or not clave_secreta.startswith('sk_test_')
            or not clave_publica.startswith('pk_test_')
        )

        try:
            if claves_stripe_invalidas and settings.DEBUG:
                numero_tarjeta = ''.join(filter(str.isdigit, request.POST.get('numero_tarjeta', '')))
                tipo_tarjeta = request.POST.get('tipo_tarjeta', '')
                banco_tarjeta = request.POST.get('banco_tarjeta', '')
                vencimiento = request.POST.get('vencimiento', '')
                cvc = request.POST.get('cvc', '')

                if len(numero_tarjeta) < 13 or tipo_tarjeta not in ('credito', 'debito') or not banco_tarjeta or len(vencimiento) != 5 or not cvc.isdigit():
                    messages.error(request, 'Completa correctamente los datos simulados de la tarjeta.')
                    return redirect('catalogo:checkout')

            cliente = obtener_o_crear_cliente(request.user)
            snapshot = [
                {
                    'producto_id': int(prod_id),
                    'nombre': datos['nombre'],
                    'cantidad': int(datos['cantidad']),
                    'precio': datos['precio'],
                }
                for prod_id, datos in carrito.items()
            ]
            pedido = Pedido.objects.create(
                numero_pedido=generar_numero_pedido(),
                cliente=cliente,
                estado='pendiente',
                total_pagado=totales['total'],
                items_snapshot=snapshot,
            )

            if claves_stripe_invalidas:
                if not settings.DEBUG:
                    pedido.delete()
                    messages.error(
                        request,
                        'Stripe sandbox no está configurado: agrega las claves sk_test_ y pk_test_ en Render.',
                    )
                    return redirect('catalogo:pago_error')

                pedido.estado = Pedido.Estado.PAGADO
                pedido.save(update_fields=['estado'])
                for item in snapshot:
                    Producto.objects.filter(
                        pk=item['producto_id'],
                        stock__gte=int(item['cantidad']),
                    ).update(stock=F('stock') - int(item['cantidad']))

                from .webhook_views import (
                    _enviar_confirmacion_compra,
                    _enviar_sms_confirmacion,
                )
                _enviar_confirmacion_compra(pedido)
                _enviar_sms_confirmacion(pedido)

                _guardar_carrito(request, {})
                messages.success(
                    request,
                    f'Modo demostración: pedido {pedido.numero_pedido} pagado correctamente.',
                )
                return redirect('catalogo:pago_exitoso', pedido_id=pedido.pk)

            monto_centavos = int(totales['total'] * 100)
            intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency='mxn',
                metadata={
                    'pedido_id': pedido.pk,
                    'pedido_num': pedido.numero_pedido,
                    'cliente': cliente.nombre,
                },
                idempotency_key=f'pedido-{pedido.pk}',
            )
            return render(request, 'catalogo/checkout.html', {
                'carrito': carrito,
                'items': items,
                'totales': totales,
                'pedido': pedido,
                'client_secret': intent.client_secret,
                'publishable_key': publishable_key,
            })
        except stripe.error.StripeError as exc:
            messages.error(request, f'Error al conectar con Stripe: {exc.user_message}')
            return redirect('catalogo:pago_error')
        except Exception as exc:
            messages.error(request, f'Error inesperado en el proceso de pago: {exc}')
            return redirect('catalogo:pago_error')

    return render(request, 'catalogo/checkout.html', {
        'carrito': carrito,
        'items': items,
        'totales': totales,
        'client_secret': None,
        'publishable_key': publishable_key,
    })


def pago_exitoso(request, pedido_id: int):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    _guardar_carrito(request, {})
    messages.success(
        request,
        f'¡Pago exitoso! Tu pedido {pedido.numero_pedido} está confirmado. '
        f'Total: ${pedido.total_pagado}',
    )
    return render(request, 'catalogo/pago_exitoso.html', {'pedido': pedido})


def pago_error(request):
    mensaje = request.GET.get('mensaje', '') or 'No pudimos procesar tu pago.'
    return render(request, 'catalogo/pago_error.html', {'mensaje': mensaje})
