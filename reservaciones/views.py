"""Módulo Reservaciones - Vistas (CRUD, cancelación y disponibilidad)."""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from habitaciones.models import Habitacion

from .forms import DisponibilidadForm, ReservacionForm
from .models import Reservacion


@login_required
def lista_reservaciones(request):
    """Listado de reservaciones con búsqueda por cliente, habitación y tipo."""
    reservaciones = Reservacion.objects.select_related('cliente', 'habitacion')

    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    estado = request.GET.get('estado', '').strip()

    if q:
        reservaciones = reservaciones.filter(
            Q(cliente__nombre__icontains=q)
            | Q(cliente__apellidos__icontains=q)
            | Q(cliente__correo__icontains=q)
            | Q(habitacion__numero__icontains=q)
        )
    if tipo:
        reservaciones = reservaciones.filter(habitacion__tipo=tipo)
    if estado:
        reservaciones = reservaciones.filter(estado=estado)

    paginator = Paginator(reservaciones, 8)
    pagina = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'reservaciones/lista.html', {
        'pagina': pagina,
        'q': q,
        'tipo': tipo,
        'estado': estado,
        'tipos': Habitacion.TIPOS,
        'estados': Reservacion._meta.get_field('estado').choices,
        'querystring': params.urlencode(),
    })


@login_required
def detalle_reservacion(request, pk):
    """Ficha de la reservación."""
    reservacion = get_object_or_404(
        Reservacion.objects.select_related('cliente', 'habitacion'), pk=pk
    )
    return render(request, 'reservaciones/detalle.html', {'reservacion': reservacion})


@login_required
def crear_reservacion(request):
    """Registro de una reservación con validación de disponibilidad."""
    iniciales = {
        'fecha_entrada': request.GET.get('entrada', ''),
        'fecha_salida': request.GET.get('salida', ''),
    }
    if request.GET.get('habitacion'):
        iniciales['habitacion'] = request.GET.get('habitacion')
    if request.GET.get('cliente'):
        iniciales['cliente'] = request.GET.get('cliente')

    if request.method == 'POST':
        form = ReservacionForm(request.POST)
        if form.is_valid():
            reservacion = form.save()
            messages.success(
                request,
                f'Reservación #{reservacion.pk} registrada. Total: ${reservacion.total} MXN.'
            )
            return redirect('reservaciones:detalle', pk=reservacion.pk)
        messages.error(request, 'Revisa los datos: no se pudo guardar la reservación.')
    else:
        form = ReservacionForm(initial=iniciales)

    return render(request, 'reservaciones/formulario.html', {
        'form': form,
        'titulo': 'Nueva reservación',
        'precios': {str(h.pk): float(h.precio_noche) for h in Habitacion.objects.all()},
    })


@login_required
def editar_reservacion(request, pk):
    """Modificación de una reservación."""
    reservacion = get_object_or_404(Reservacion, pk=pk)
    if reservacion.estado == 'Cancelada':
        messages.error(request, 'No se puede modificar una reservación cancelada.')
        return redirect('reservaciones:detalle', pk=reservacion.pk)

    if request.method == 'POST':
        form = ReservacionForm(request.POST, instance=reservacion)
        if form.is_valid():
            form.save()
            messages.success(request, f'La reservación #{reservacion.pk} se actualizó correctamente.')
            return redirect('reservaciones:detalle', pk=reservacion.pk)
        messages.error(request, 'Revisa los datos: no se pudo guardar la reservación.')
    else:
        form = ReservacionForm(instance=reservacion)

    return render(request, 'reservaciones/formulario.html', {
        'form': form,
        'titulo': f'Editar reservación #{reservacion.pk}',
        'reservacion': reservacion,
        'precios': {str(h.pk): float(h.precio_noche) for h in Habitacion.objects.all()},
    })


@login_required
@require_POST
def cancelar_reservacion(request, pk):
    """Cambia el estado de la reservación a Cancelada."""
    reservacion = get_object_or_404(Reservacion, pk=pk)
    if reservacion.estado == 'Cancelada':
        messages.warning(request, 'La reservación ya estaba cancelada.')
    elif reservacion.estado == 'Finalizada':
        messages.error(request, 'No se puede cancelar una reservación finalizada.')
    else:
        reservacion.estado = 'Cancelada'
        reservacion.save()
        messages.success(request, f'La reservación #{reservacion.pk} se canceló correctamente.')
    return redirect('reservaciones:detalle', pk=reservacion.pk)


@login_required
def consultar_disponibilidad(request):
    """Consulta de habitaciones libres en un rango de fechas."""
    resultados = None
    form = DisponibilidadForm(request.GET or None)

    if request.GET and form.is_valid():
        entrada = form.cleaned_data['fecha_entrada']
        salida = form.cleaned_data['fecha_salida']
        tipo = form.cleaned_data.get('tipo')
        capacidad = form.cleaned_data.get('capacidad')

        habitaciones = Habitacion.objects.filter(disponible=True)
        if tipo:
            habitaciones = habitaciones.filter(tipo=tipo)
        if capacidad:
            habitaciones = habitaciones.filter(capacidad__gte=capacidad)

        resultados = []
        for habitacion in habitaciones:
            if habitacion.esta_disponible_en(entrada, salida):
                noches = (salida - entrada).days
                resultados.append({
                    'habitacion': habitacion,
                    'noches': noches,
                    'total': Decimal(noches) * habitacion.precio_noche,
                })

        resultados.sort(key=lambda r: r['habitacion'].precio_noche)

    return render(request, 'reservaciones/disponibilidad.html', {
        'form': form,
        'resultados': resultados,
        'consultado': bool(request.GET),
    })
