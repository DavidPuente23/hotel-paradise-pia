"""Módulo Dashboard y Reportes - Vistas.

Integrante 5: reportes y estadísticas.
Integrante 4: dashboard principal.
"""

import csv
from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render

from clientes.models import Cliente
from habitaciones.models import Habitacion
from reservaciones.models import Reservacion

ESTADOS_CON_INGRESO = ['Confirmada', 'Finalizada']


def _ingresos_totales():
    total = Reservacion.objects.filter(estado__in=ESTADOS_CON_INGRESO).aggregate(
        total=Sum('total')
    )['total']
    return total or Decimal('0.00')


@login_required
def dashboard(request):
    """Panel principal con los indicadores del hotel."""
    hoy = date.today()

    total_clientes = Cliente.objects.count()
    total_habitaciones = Habitacion.objects.count()
    total_reservaciones = Reservacion.objects.count()
    habitaciones_disponibles = Habitacion.objects.filter(disponible=True).count()
    ingresos = _ingresos_totales()

    reservaciones_activas = Reservacion.objects.filter(
        estado__in=['Pendiente', 'Confirmada'], fecha_salida__gte=hoy
    ).count()

    # Ocupación de hoy: habitaciones con una reservación vigente
    ocupadas_hoy = Habitacion.objects.filter(
        reservaciones__estado__in=['Confirmada'],
        reservaciones__fecha_entrada__lte=hoy,
        reservaciones__fecha_salida__gt=hoy,
    ).distinct().count()
    porcentaje_ocupacion = 0
    if total_habitaciones:
        porcentaje_ocupacion = round((ocupadas_hoy * 100) / total_habitaciones)

    ultimas_reservaciones = Reservacion.objects.select_related('cliente', 'habitacion').order_by(
        '-fecha_creacion'
    )[:6]
    proximas_entradas = Reservacion.objects.select_related('cliente', 'habitacion').filter(
        estado__in=['Pendiente', 'Confirmada'],
        fecha_entrada__gte=hoy,
    ).order_by('fecha_entrada')[:5]

    return render(request, 'core/dashboard.html', {
        'total_clientes': total_clientes,
        'total_habitaciones': total_habitaciones,
        'total_reservaciones': total_reservaciones,
        'habitaciones_disponibles': habitaciones_disponibles,
        'ingresos': ingresos,
        'reservaciones_activas': reservaciones_activas,
        'ocupadas_hoy': ocupadas_hoy,
        'porcentaje_ocupacion': porcentaje_ocupacion,
        'ultimas_reservaciones': ultimas_reservaciones,
        'proximas_entradas': proximas_entradas,
        'hoy': hoy,
    })


@login_required
def reportes(request):
    """Reportes y estadísticas del hotel."""
    por_estado = (
        Reservacion.objects.values('estado')
        .annotate(cantidad=Count('id'), ingresos=Sum('total'))
        .order_by('estado')
    )

    por_tipo = (
        Reservacion.objects.values('habitacion__tipo')
        .annotate(
            cantidad=Count('id'),
            ingresos=Sum('total', filter=Q(estado__in=ESTADOS_CON_INGRESO)),
        )
        .order_by('habitacion__tipo')
    )

    ingresos_mes = (
        Reservacion.objects.filter(estado__in=ESTADOS_CON_INGRESO)
        .annotate(mes=TruncMonth('fecha_entrada'))
        .values('mes')
        .annotate(cantidad=Count('id'), ingresos=Sum('total'))
        .order_by('-mes')[:12]
    )
    ingresos_mes = [
        {
            'mes': fila['mes'].strftime('%m/%Y') if fila['mes'] else '-',
            'cantidad': fila['cantidad'],
            'ingresos': fila['ingresos'],
        }
        for fila in ingresos_mes
    ]

    top_clientes = (
        Cliente.objects.annotate(
            num_reservaciones=Count('reservaciones'),
            gasto=Sum('reservaciones__total', filter=Q(reservaciones__estado__in=ESTADOS_CON_INGRESO)),
        )
        .filter(num_reservaciones__gt=0)
        .order_by('-gasto')[:5]
    )

    habitaciones_top = (
        Habitacion.objects.annotate(num_reservaciones=Count('reservaciones'))
        .filter(num_reservaciones__gt=0)
        .order_by('-num_reservaciones', 'numero')[:5]
    )

    return render(request, 'core/reportes.html', {
        'por_estado': por_estado,
        'por_tipo': por_tipo,
        'ingresos_mes': ingresos_mes,
        'top_clientes': top_clientes,
        'habitaciones_top': habitaciones_top,
        'ingresos_totales': _ingresos_totales(),
        'total_reservaciones': Reservacion.objects.count(),
        'total_clientes': Cliente.objects.count(),
    })


@login_required
def exportar_reservaciones_csv(request):
    """Descarga el listado de reservaciones en formato CSV."""
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = 'attachment; filename="reporte_reservaciones.csv"'
    respuesta.write('\ufeff')  # BOM para que Excel muestre bien los acentos

    escritor = csv.writer(respuesta)
    escritor.writerow([
        'ID', 'Cliente', 'Correo', 'Habitación', 'Tipo',
        'Fecha entrada', 'Fecha salida', 'Noches', 'Total', 'Estado',
    ])

    reservaciones = Reservacion.objects.select_related('cliente', 'habitacion')
    for reservacion in reservaciones:
        escritor.writerow([
            reservacion.pk,
            str(reservacion.cliente),
            reservacion.cliente.correo,
            reservacion.habitacion.numero,
            reservacion.habitacion.tipo,
            reservacion.fecha_entrada.strftime('%d/%m/%Y'),
            reservacion.fecha_salida.strftime('%d/%m/%Y'),
            reservacion.noches,
            reservacion.total,
            reservacion.estado,
        ])

    return respuesta
