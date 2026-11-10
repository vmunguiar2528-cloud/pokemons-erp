from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    empresa = models.CharField(max_length=150, blank=True, null=True)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.empresa or 'Particular'}"