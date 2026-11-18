from django.contrib import admin
from .models import Venta, DetalleVenta, Pedido

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'metodo_pago', 'monto_pagado', 'referencia_transferencia', 'ultimos4_tarjeta', 'total')
    inlines = [DetalleVentaInline]
    actions = ['delete_selected']
    can_delete = True

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'cliente', 'estado', 'total_pagado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('numero_pedido', 'cliente__nombre', 'cliente__correo')
    actions = ['delete_selected']
    can_delete = True