from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProveedorForm
from .models import Proveedor


def lista_proveedores(request):
  proveedores = Proveedor.objects.all()
  return render(
      request, 'proveedores/lista.html', {'proveedores': proveedores}
  )


def detalle_proveedor(request, pk):
  proveedor = get_object_or_404(Proveedor, pk=pk)
  return render(request, 'proveedores/detalle.html', {'proveedor': proveedor})


def crear_proveedor(request):
  form = ProveedorForm(request.POST or None)
  if form.is_valid():
    form.save()
    messages.success(request, 'Proveedor guardado correctamente.')
    return redirect('proveedores:lista')
  return render(
      request,
      'proveedores/form.html',
      {'form': form, 'titulo': 'Nuevo Proveedor'},
  )


def editar_proveedor(request, pk):
  proveedor = get_object_or_404(Proveedor, pk=pk)
  form = ProveedorForm(request.POST or None, instance=proveedor)
  if form.is_valid():
    form.save()
    messages.success(request, 'Proveedor actualizado correctamente.')
    return redirect('proveedores:lista')
  return render(
      request,
      'proveedores/form.html',
      {'form': form, 'titulo': 'Editar Proveedor'},
  )


def eliminar_proveedor(request, pk):
  proveedor = get_object_or_404(Proveedor, pk=pk)
  if request.method == 'POST':
    proveedor.delete()
    messages.success(request, 'Proveedor eliminado correctamente.')
    return redirect('proveedores:lista')
  return render(
      request,
      'proveedores/confirmar_eliminar.html',
      {'objeto': proveedor, 'titulo': 'Eliminar Proveedor'},
  )