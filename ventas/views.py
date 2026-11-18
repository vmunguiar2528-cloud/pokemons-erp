import json

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import VentaForm
from .models import DetalleVenta, Venta


def lista_ventas(request):
  ventas = Venta.objects.all().order_by('-fecha')
  return render(request, 'ventas/lista.html', {'ventas': ventas})


def crear_venta(request):
  if request.method == 'POST':
    form = VentaForm(request.POST)
    if form.is_valid():
      cliente = form.cleaned_data['cliente']
      producto = form.cleaned_data['producto']
      cantidad = form.cleaned_data['cantidad']
      metodo_pago = form.cleaned_data['metodo_pago']
      monto_pagado = form.cleaned_data.get('monto_pagado')
      referencia_transferencia = form.cleaned_data.get('referencia_transferencia', '')
      numero_tarjeta = form.cleaned_data.get('numero_tarjeta', '')
      numero_tarjeta = ''.join(caracter for caracter in numero_tarjeta if caracter.isdigit())
      ultimos4_tarjeta = numero_tarjeta[-4:] if numero_tarjeta else ''
      titular_tarjeta = ''
      vencimiento_tarjeta = ''

      if producto.stock >= cantidad:
        total_venta = producto.precio * cantidad

        venta = Venta.objects.create(
            cliente=cliente,
            total=total_venta,
            metodo_pago=metodo_pago,
            monto_pagado=monto_pagado,
            referencia_transferencia=referencia_transferencia,
            titular_tarjeta=titular_tarjeta,
            ultimos4_tarjeta=ultimos4_tarjeta,
            vencimiento_tarjeta=vencimiento_tarjeta,
        )
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
        )

        producto.stock -= cantidad
        producto.save()
        messages.success(
            request, f'Venta registrada con éxito. Stock de {producto.nombre} actualizado.'
        )
        return redirect('ventas:lista')
      else:
        messages.error(
            request,
            f'Stock insuficiente para {producto.nombre}. Disponible:'
            f' {producto.stock}',
        )
  else:
    form = VentaForm()

  precios = {
      str(producto.pk): str(producto.precio)
      for producto in form.fields['producto'].queryset
  }

  return render(
      request,
      'ventas/form.html',
      {
          'form': form,
          'titulo': 'Registrar Nueva Venta',
          'precios_json': json.dumps(precios),
      },
  )