import os
import openpyxl
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from clientes.models import Cliente
from productos.models import Producto
from ventas.models import Venta
from configuracion.models import ConfiguracionERP


def dashboard(request):
  total_clientes = Cliente.objects.count()
  total_productos = Producto.objects.count()
  total_ventas_count = Venta.objects.count()

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

  ws.append(['ID', 'Producto', 'Categoría', 'Precio', 'Stock'])

  for p in Producto.objects.all():
    cat = p.categoria.nombre if p.categoria else 'Sin categoría'
    ws.append([p.id, p.nombre, cat, float(p.precio), p.stock])

  response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  response['Content-Disposition'] = 'attachment; filename="inventario_productos.xlsx"'
  wb.save(response)
  return response


def exportar_pdf_ventas(request):
  venta_id = request.GET.get('venta_id')
  ventas = Venta.objects.select_related('cliente').order_by('-fecha')

  if venta_id:
    ventas = ventas.filter(id=venta_id)

  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

  total_ventas = ventas.count()
  ingresos_totales = sum(v.total for v in ventas)
  empresa = ConfiguracionERP.get_instance()
  nombre_empresa = (empresa.nombre_empresa or 'Mi Empresa').strip() or 'Mi Empresa'

  p = canvas.Canvas(response, pagesize=letter)
  width, height = letter

  p.setStrokeColor(colors.HexColor('#2563EB'))
  p.setLineWidth(1.2)
  p.rect(30, 30, 552, 732, stroke=1, fill=0)

  pikachu_path = os.path.join(str(settings.BASE_DIR), 'static', 'images', 'pikachu.png')
  if os.path.exists(pikachu_path):
    p.saveState()
    p.setFillAlpha(0.10)
    p.drawImage(pikachu_path, 0, 0, width=612, height=792)
    p.restoreState()

  blue = colors.HexColor('#2563EB')
  dark = colors.HexColor('#111827')
  soft = colors.HexColor('#E5E7EB')

  p.setFillColor(blue)
  p.setFont('Helvetica-Bold', 22)
  p.drawString(62, 748, nombre_empresa.upper())
  p.setFont('Helvetica-Bold', 14)
  p.drawString(62, 725, 'REPORTE DE VENTAS')

  p.setFillColor(dark)
  p.setFont('Helvetica', 11)
  p.drawString(62, 695, f'Total de ventas registradas: {total_ventas}')
  p.drawString(62, 680, f'Ingresos totales: ${ingresos_totales:,.2f}')

  p.setFillColor(blue)
  p.setFont('Helvetica-Bold', 12)
  p.drawString(420, 695, 'Música')

  p.setStrokeColor(blue)
  p.setLineWidth(1)
  p.rect(410, 670, 110, 18, stroke=1, fill=0)
  p.setFillColor(dark)
  p.setFont('Helvetica', 9)
  p.drawString(418, 676, 'Archivo de audio')

  p.setFillColor(blue)
  p.setFont('Helvetica-Bold', 10)
  p.drawString(60, 646, 'N°')
  p.drawString(95, 646, 'CLIENTE')
  p.drawString(290, 646, 'FECHA')
  p.drawString(390, 646, 'PAGO')
  p.drawString(500, 646, 'TOTAL')

  y = 618
  if total_ventas == 0:
    p.setFillColor(blue)
    p.setFont('Helvetica-Bold', 16)
    p.drawString(190, 540, 'NO HAY VENTAS REGISTRADAS')
  else:
    for index, venta in enumerate(ventas, start=1):
      if y < 90:
        p.showPage()
        y = 760

      p.setStrokeColor(blue)
      p.rect(50, y - 25, 510, 34, stroke=1, fill=0)
      p.setFillColor(dark)
      p.setFont('Helvetica', 10)
      p.drawString(60, y - 8, str(index))
      p.drawString(95, y - 8, (venta.cliente.nombre or 'Cliente')[:28])
      p.drawString(290, y - 8, venta.fecha.strftime('%d/%m/%Y %H:%M'))
      p.drawString(390, y - 8, venta.get_metodo_pago_display()[:14])
      p.drawString(500, y - 8, f'${venta.total:,.2f}')
      y -= 38

  p.setFillColor(blue)
  p.setStrokeColor(blue)
  p.rect(50, 38, 510, 20, stroke=1, fill=0)
  p.setFont('Helvetica-Bold', 10)
  p.drawString(60, 45, f'{nombre_empresa} - Reporte generado automáticamente')

  p.showPage()
  p.save()
  return response


def home(request):
  return render(request, 'inicio.html')