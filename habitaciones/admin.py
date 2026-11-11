"""Panel de administración del módulo Habitaciones."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Habitacion


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'precio_noche', 'capacidad', 'disponible', 'vista_previa')
    list_filter = ('tipo', 'disponible')
    search_fields = ('numero', 'tipo', 'descripcion')
    list_editable = ('disponible',)
    ordering = ('numero',)
    fieldsets = (
        ('Datos de la habitación', {
            'fields': ('numero', 'tipo', 'precio_noche', 'capacidad', 'disponible')
        }),
        ('Fotografía y descripción', {
            'fields': ('imagen', 'descripcion')
        }),
    )

    @admin.display(description='Imagen')
    def vista_previa(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.imagen.url)
        return 'Sin imagen'
