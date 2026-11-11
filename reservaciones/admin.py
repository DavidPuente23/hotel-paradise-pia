"""Panel de administración del módulo Reservaciones."""

from django.contrib import admin

from .models import Reservacion


@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'habitacion', 'fecha_entrada', 'fecha_salida', 'total', 'estado')
    list_filter = ('estado', 'habitacion__tipo', 'fecha_entrada')
    search_fields = ('cliente__nombre', 'cliente__apellidos', 'habitacion__numero')
    autocomplete_fields = ('cliente', 'habitacion')
    readonly_fields = ('total', 'fecha_creacion')
    date_hierarchy = 'fecha_entrada'
    ordering = ('-fecha_entrada',)
    actions = ('marcar_canceladas',)

    @admin.action(description='Marcar reservaciones seleccionadas como canceladas')
    def marcar_canceladas(self, request, queryset):
        actualizadas = queryset.exclude(estado='Cancelada').update(estado='Cancelada')
        self.message_user(request, f'Se cancelaron {actualizadas} reservación(es).')
