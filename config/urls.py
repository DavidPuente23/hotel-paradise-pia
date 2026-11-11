"""Rutas principales del proyecto Hotel Paradise."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('habitaciones/', include('habitaciones.urls')),
    path('clientes/', include('clientes.urls')),
    path('reservaciones/', include('reservaciones.urls')),
    path('cuentas/', include('cuentas.urls')),
]

# Servir archivos subidos (imágenes de habitaciones) en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
