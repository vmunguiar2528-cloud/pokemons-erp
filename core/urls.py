from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# PERSONALIZACIÓN DEL ENCABEZADO Y TÍTULOS DE POKEADMIN
admin.site.site_header = '⚡ POKÉMONS ERP — PokeAdmin Center'
admin.site.site_title = 'Pokémons ERP'
admin.site.index_title = (
    'Panel de Administración Oficial — Victor Munguía'
)

# INYECCIÓN DIRECTA DE ESTILOS CSS AL ADMIN
admin.autodiscover()
admin.site.enable_nav_sidebar = True

# Añadir el archivo CSS personalizado al formulario del Admin
admin.site.site_url = '/'


class CustomAdminSite(admin.AdminSite):

  class Media:
    css = {'all': ('admin/css/custom_admin.css',)}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reportes.urls')),
    path('clientes/', include('clientes.urls')),
    path('productos/', include('productos.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('ventas/', include('ventas.urls')),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)