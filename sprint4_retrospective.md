# Sprint 4 Retrospective — ERP Django

## ¿Qué funcionó bien?
1. El snapshot de items conserva la compra aunque se vacíe el carrito.
2. El webhook verifica la firma antes de modificar pedidos.
3. La expresión F() permite descontar stock de forma atómica.

## ¿Qué mejorar?
1. Mostrar un loader más visible durante el confirmCardPayment.
2. Documentar el diagrama completo de Stripe y webhooks.

## Kaizen para Sprint 5
Crear primero las pruebas de tareas asíncronas antes de implementar el envío de correo.
