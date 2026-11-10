from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductoForm
from .models import Producto


def lista_productos(request):
  productos = Producto.objects.all()
  return render(request, 'productos/lista.html', {'productos': productos})


def detalle_producto(request, pk):
  producto = get_object_or_404(Producto, pk=pk)
  return render(request, 'productos/detalle.html', {'producto': producto})


def crear_producto(request):
  form = ProductoForm(request.POST or None, request.FILES or None)
  if form.is_valid():
    form.save()
    messages.success(request, 'Producto guardado exitosamente.')
    return redirect('productos:lista')
  return render(
      request,
      'productos/form.html',
      {'form': form, 'titulo': 'Nuevo Producto'},
  )


def editar_producto(request, pk):
  producto = get_object_or_404(Producto, pk=pk)
  form = ProductoForm(
      request.POST or None, request.FILES or None, instance=producto
  )
  if form.is_valid():
    form.save()
    messages.success(request, 'Producto actualizado exitosamente.')
    return redirect('productos:lista')
  return render(
      request,
      'productos/form.html',
      {'form': form, 'titulo': 'Editar Producto'},
  )


def eliminar_producto(request, pk):
  producto = get_object_or_404(Producto, pk=pk)
  if request.method == 'POST':
    producto.delete()
    messages.success(request, 'Producto eliminado exitosamente.')
    return redirect('productos:lista')
  return render(
      request,
      'productos/confirmar_eliminar.html',
      {'objeto': producto, 'titulo': 'Eliminar Producto'},
  )