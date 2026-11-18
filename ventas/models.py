from django.db import models
from clientes.models import Cliente
from productos.models import Producto

class Venta(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'efectivo', 'Efectivo'
        TARJETA = 'tarjeta', 'Tarjeta'
        TRANSFERENCIA = 'transferencia', 'Transferencia'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO,
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    referencia_transferencia = models.CharField(max_length=100, blank=True)
    titular_tarjeta = models.CharField(max_length=150, blank=True)
    ultimos4_tarjeta = models.CharField(max_length=4, blank=True)
    vencimiento_tarjeta = models.CharField(max_length=7, blank=True)

    def __str__(self):
        return f"Venta #{self.pk:05d} - {self.cliente.nombre}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de pago'
        PAGADO = 'pagado', 'Pagado'
        CANCELADO = 'cancelado', 'Cancelado'

    numero_pedido = models.CharField(max_length=30, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    total_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    items_snapshot = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Snapshot de items del carrito',
        help_text='Copia del carrito al momento de crear el pedido.',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.numero_pedido} - {self.get_estado_display()}'