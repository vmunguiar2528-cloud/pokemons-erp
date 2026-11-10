from django.contrib import admin
from .models import ConfiguracionERP

@admin.register(ConfiguracionERP)
class ConfiguracionERPAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'rfc', 'moneda', 'iva_porcentaje')