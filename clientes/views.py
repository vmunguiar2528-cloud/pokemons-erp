from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm
from .models import Cliente


def lista_clientes(request):
  clientes = Cliente.objects.all()
  return render(request, 'clientes/lista.html', {'clientes': clientes})


def detalle_cliente(request, pk):
  cliente = get_object_or_404(Cliente, pk=pk)
  return render(request, 'clientes/detalle.html', {'cliente': cliente})


def crear_cliente(request):
  form = ClienteForm(request.POST or None)
  if form.is_valid():
    form.save()
    messages.success(request, 'Cliente registrado correctamente.')
    return redirect('clientes:lista')
  return render(
      request,
      'clientes/form.html',
      {'form': form, 'titulo': 'Nuevo Cliente'},
  )


def editar_cliente(request, pk):
  cliente = get_object_or_404(Cliente, pk=pk)
  form = ClienteForm(request.POST or None, instance=cliente)
  if form.is_valid():
    form.save()
    messages.success(request, 'Cliente actualizado correctamente.')
    return redirect('clientes:lista')
  return render(
      request,
      'clientes/form.html',
      {'form': form, 'titulo': 'Editar Cliente'},
  )


def eliminar_cliente(request, pk):
  cliente = get_object_or_404(Cliente, pk=pk)
  if request.method == 'POST':
    cliente.delete()
    messages.success(request, 'Cliente eliminado correctamente.')
    return redirect('clientes:lista')
  return render(
      request,
      'clientes/confirmar_eliminar.html',
      {'objeto': cliente, 'titulo': 'Eliminar Cliente'},
  )