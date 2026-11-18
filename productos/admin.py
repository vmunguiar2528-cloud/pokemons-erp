from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    actions = ['delete_selected']
    can_delete = True

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'precio', 'stock', 'imagen_preview')
    list_filter = ('categoria', 'proveedor')
    search_fields = ('nombre',)
    actions = ['delete_selected']
    can_delete = True

    def imagen_preview(self, obj):
        if not obj.imagen:
            return 'Sin imagen'
        return format_html('<img src="{}" style="max-height: 60px; max-width: 100px; border-radius: 6px;" />', obj.imagen.url)

    imagen_preview.short_description = 'Imagen'