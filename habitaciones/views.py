"""Módulo Habitaciones - Vistas (CRUD, búsqueda y tipos)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import HabitacionForm
from .models import Habitacion


@login_required
def lista_habitaciones(request):
    """Listado y búsqueda de habitaciones."""
    habitaciones = Habitacion.objects.all()

    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    disponible = request.GET.get('disponible', '').strip()

    if q:
        habitaciones = habitaciones.filter(
            Q(numero__icontains=q) | Q(tipo__icontains=q) | Q(descripcion__icontains=q)
        )
    if tipo:
        habitaciones = habitaciones.filter(tipo=tipo)
    if disponible == '1':
        habitaciones = habitaciones.filter(disponible=True)
    elif disponible == '0':
        habitaciones = habitaciones.filter(disponible=False)

    paginator = Paginator(habitaciones, 8)
    pagina = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'habitaciones/lista.html', {
        'pagina': pagina,
        'q': q,
        'tipo': tipo,
        'disponible': disponible,
        'tipos': Habitacion.TIPOS,
        'querystring': params.urlencode(),
    })


@login_required
def detalle_habitacion(request, pk):
    """Ficha de una habitación con sus reservaciones."""
    habitacion = get_object_or_404(Habitacion, pk=pk)
    reservaciones = habitacion.reservaciones.select_related('cliente').order_by('-fecha_entrada')
    return render(request, 'habitaciones/detalle.html', {
        'habitacion': habitacion,
        'reservaciones': reservaciones,
    })


@login_required
def crear_habitacion(request):
    """Alta de una habitación."""
    if request.method == 'POST':
        form = HabitacionForm(request.POST, request.FILES)
        if form.is_valid():
            habitacion = form.save()
            messages.success(request, f'La habitación {habitacion.numero} se registró correctamente.')
            return redirect('habitaciones:lista')
    else:
        form = HabitacionForm()
    return render(request, 'habitaciones/formulario.html', {'form': form, 'titulo': 'Nueva habitación'})


@login_required
def editar_habitacion(request, pk):
    """Modificación de una habitación."""
    habitacion = get_object_or_404(Habitacion, pk=pk)
    if request.method == 'POST':
        form = HabitacionForm(request.POST, request.FILES, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, f'La habitación {habitacion.numero} se actualizó correctamente.')
            return redirect('habitaciones:detalle', pk=habitacion.pk)
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, 'habitaciones/formulario.html', {
        'form': form,
        'titulo': f'Editar habitación {habitacion.numero}',
        'habitacion': habitacion,
    })


@login_required
def eliminar_habitacion(request, pk):
    """Elimina una habitación (Regla 5: no si tiene reservaciones activas)."""
    habitacion = get_object_or_404(Habitacion, pk=pk)

    if request.method == 'POST':
        if habitacion.tiene_reservaciones_activas():
            messages.error(
                request,
                f'No se puede eliminar la habitación {habitacion.numero}: tiene reservaciones activas. '
                'Primero cancela o finaliza esas reservaciones.'
            )
            return redirect('habitaciones:detalle', pk=habitacion.pk)
        try:
            numero = habitacion.numero
            habitacion.delete()
            messages.success(request, f'La habitación {numero} se eliminó correctamente.')
            return redirect('habitaciones:lista')
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar la habitación porque tiene reservaciones registradas en el historial.'
            )
            return redirect('habitaciones:detalle', pk=habitacion.pk)

    return render(request, 'habitaciones/confirmar_eliminar.html', {'habitacion': habitacion})


@login_required
def tipos_habitacion(request):
    """Administración / resumen de los tipos de habitación."""
    resumen = (
        Habitacion.objects.values('tipo')
        .annotate(
            total=Count('id'),
            disponibles=Count('id', filter=Q(disponible=True)),
            precio_promedio=Avg('precio_noche'),
        )
        .order_by('tipo')
    )
    # Respetamos el orden definido en las choices
    orden = [t[0] for t in Habitacion.TIPOS]
    resumen = sorted(resumen, key=lambda r: orden.index(r['tipo']))
    return render(request, 'habitaciones/tipos.html', {'resumen': resumen})
