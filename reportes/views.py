import openpyxl
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.pdfgen import canvas

from clientes.models import Cliente
from productos.models import Producto
from ventas.models import Venta


def dashboard(request):
  total_clientes = Cliente.objects.count()
  total_productos = Producto.objects.count()
  total_ventas_count = Venta.objects.count()

  # Calcular ingresos totales sumando todas las ventas
  ventas = Venta.objects.all()
  ingresos_totales = sum(v.total for v in ventas)

  context = {
      'total_clientes': total_clientes,
      'total_productos': total_productos,
      'total_ventas_count': total_ventas_count,
      'ingresos_totales': ingresos_totales,
  }
  return render(request, 'reportes/dashboard.html', context)


def exportar_excel_productos(request):
  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = 'Inventario'

  # Encabezados de la tabla
  ws.append(['ID', 'Producto', 'Categoría', 'Precio', 'Stock'])

  for p in Producto.objects.all():
    cat = p.categoria.nombre if p.categoria else 'Sin categoría'
    ws.append([p.id, p.nombre, cat, float(p.precio), p.stock])

  response = HttpResponse(
      content_type=(
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      )
  )
  response['Content-Disposition'] = (
      'attachment; filename="inventario_productos.xlsx"'
  )
  wb.save(response)
  return response


def exportar_pdf_ventas(request):
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = (
      'attachment; filename="reporte_ventas.pdf"'
  )

  p = canvas.Canvas(response)
  p.drawString(100, 800, '=== REPORTE DE VENTAS — ERP ===')

  y = 750
  for v in Venta.objects.all():
    fecha_str = v.fecha.strftime('%Y-%m-%d %H:%M')
    linea = (
        f'Venta #{v.id} | Cliente: {v.cliente.nombre} | Fecha: {fecha_str} |'
        f' Total: ${v.total}'
    )
    p.drawString(100, y, linea)
    y -= 20
    if y < 50:
      p.showPage()
      y = 800

  p.showPage()
  p.save()
  return response
def home(request):
  return render(request, 'inicio.html')