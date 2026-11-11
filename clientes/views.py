"""Módulo Clientes - Vistas (CRUD y búsqueda)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm
from .models import Cliente


@login_required
def lista_clientes(request):
    """Listado y búsqueda de clientes por nombre, apellidos, correo o teléfono."""
    clientes = Cliente.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        clientes = clientes.filter(
            Q(nombre__icontains=q)
            | Q(apellidos__icontains=q)
            | Q(correo__icontains=q)
            | Q(telefono__icontains=q)
        )

    paginator = Paginator(clientes, 8)
    pagina = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'clientes/lista.html', {
        'pagina': pagina,
        'q': q,
        'querystring': params.urlencode(),
        'total': clientes.count(),
    })


@login_required
def detalle_cliente(request, pk):
    """Ficha del cliente con su historial de reservaciones."""
    cliente = get_object_or_404(Cliente, pk=pk)
    reservaciones = cliente.reservaciones.select_related('habitacion').order_by('-fecha_entrada')
    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'reservaciones': reservaciones,
    })


@login_required
def crear_cliente(request):
    """Alta de un cliente."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'El cliente {cliente} se registró correctamente.')
            return redirect('clientes:lista')
    else:
        form = ClienteForm()
    return render(request, 'clientes/formulario.html', {'form': form, 'titulo': 'Nuevo cliente'})


@login_required
def editar_cliente(request, pk):
    """Modificación de un cliente."""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'El cliente {cliente} se actualizó correctamente.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': f'Editar cliente: {cliente}',
        'cliente': cliente,
    })


@login_required
def eliminar_cliente(request, pk):
    """Elimina un cliente si no tiene reservaciones registradas."""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            nombre = str(cliente)
            cliente.delete()
            messages.success(request, f'El cliente {nombre} se eliminó correctamente.')
            return redirect('clientes:lista')
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar el cliente porque tiene reservaciones registradas. '
                'Conserva el historial del hotel.'
            )
            return redirect('clientes:detalle', pk=cliente.pk)
    return render(request, 'clientes/confirmar_eliminar.html', {'cliente': cliente})
