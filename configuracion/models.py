from django.db import models

class ConfiguracionERP(models.Model):
    nombre_empresa = models.CharField(max_length=150, default="Mi Empresa ERP")
    rfc = models.CharField(max_length=20, blank=True, null=True)
    moneda = models.CharField(max_length=10, default="MXN")
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    logo = models.ImageField(upload_to="logo/", blank=True, null=True)

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.nombre_empresa