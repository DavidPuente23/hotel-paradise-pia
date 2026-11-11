"""Módulo Reservaciones - Modelos.

Integrante 3: modelo Reservación, validación de fechas y disponibilidad.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from clientes.models import Cliente
from habitaciones.models import Habitacion

ESTADOS = [
    ('Pendiente', 'Pendiente'),
    ('Confirmada', 'Confirmada'),
    ('Cancelada', 'Cancelada'),
    ('Finalizada', 'Finalizada'),
]

# Estados que ocupan la habitación en el calendario
ESTADOS_ACTIVOS = ['Pendiente', 'Confirmada']


class Reservacion(models.Model):
    """Reservación de una habitación por un cliente."""

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='reservaciones',
        verbose_name='Cliente',
    )
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,
        related_name='reservaciones',
        verbose_name='Habitación',
    )
    fecha_entrada = models.DateField('Fecha de entrada')
    fecha_salida = models.DateField('Fecha de salida')
    total = models.DecimalField(
        'Total',
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text='Se calcula automáticamente: noches × precio por noche.',
    )
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='Pendiente')
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'
        ordering = ['-fecha_entrada']

    def __str__(self):
        return f'Reservación #{self.pk} - {self.cliente}'

    def get_absolute_url(self):
        return reverse('reservaciones:detalle', args=[self.pk])

    @property
    def noches(self):
        """Número de noches de la estancia."""
        if self.fecha_entrada and self.fecha_salida:
            return (self.fecha_salida - self.fecha_entrada).days
        return 0

    def clean(self):
        """Reglas de negocio 1 y 2."""
        super().clean()

        # Regla 2: la fecha de salida debe ser mayor que la entrada
        if self.fecha_entrada and self.fecha_salida:
            if self.fecha_salida <= self.fecha_entrada:
                raise ValidationError(
                    {'fecha_salida': 'La fecha de salida debe ser mayor que la fecha de entrada.'}
                )

        if not self.habitacion_id or not self.fecha_entrada or not self.fecha_salida:
            return

        # No se puede reservar una habitación marcada como no disponible
        if not self.habitacion.disponible:
            raise ValidationError(
                {'habitacion': 'Esta habitación está marcada como NO disponible.'}
            )

        # Regla 1: no puede haber dos reservaciones en las mismas fechas
        choques = Reservacion.objects.filter(
            habitacion=self.habitacion,
            estado__in=ESTADOS_ACTIVOS,
            fecha_entrada__lt=self.fecha_salida,
            fecha_salida__gt=self.fecha_entrada,
        )
        if self.pk:
            choques = choques.exclude(pk=self.pk)
        if choques.exists():
            otra = choques.first()
            raise ValidationError(
                {
                    'habitacion': (
                        f'La habitación {self.habitacion.numero} ya está reservada '
                        f'del {otra.fecha_entrada.strftime("%d/%m/%Y")} al '
                        f'{otra.fecha_salida.strftime("%d/%m/%Y")}.'
                    )
                }
            )

    def save(self, *args, **kwargs):
        # Calculamos el total automáticamente
        if self.fecha_entrada and self.fecha_salida and self.habitacion_id:
            noches = (self.fecha_salida - self.fecha_entrada).days
            if noches > 0:
                self.total = Decimal(noches) * self.habitacion.precio_noche
        super().save(*args, **kwargs)

    def es_activa(self):
        return self.estado in ESTADOS_ACTIVOS
