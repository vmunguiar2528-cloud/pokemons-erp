from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import VentaForm
from .models import Venta


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

      if producto.stock >= cantidad:
        total_venta = producto.precio * cantidad
        producto.stock -= cantidad
        producto.save()

        Venta.objects.create(cliente=cliente, total=total_venta)
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

  return render(
      request,
      'ventas/form.html',
      {'form': form, 'titulo': 'Registrar Nueva Venta'},
  )