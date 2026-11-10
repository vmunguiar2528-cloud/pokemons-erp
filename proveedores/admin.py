from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'empresa', 'correo', 'telefono')
    search_fields = ('nombre', 'empresa')