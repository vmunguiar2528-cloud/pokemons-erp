import os
import filetype
from django.core.exceptions import ValidationError
from django.db import models
from proveedores.models import Proveedor


def validate_product_image(file):
    max_size = 2 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError('La imagen debe pesar menos de 2 MB.')

    try:
        file.seek(0)
        kind = filetype.guess(file.read())
        file.seek(0)
        if kind is None:
            raise ValidationError('El archivo no es una imagen válida.')
        if kind.mime not in {'image/jpeg', 'image/png', 'image/webp'}:
            raise ValidationError('Solo se permiten imágenes JPG, PNG o WEBP.')
    except Exception:
        file.seek(0)
        raise ValidationError('No se pudo validar la imagen.')


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, validators=[validate_product_image])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre