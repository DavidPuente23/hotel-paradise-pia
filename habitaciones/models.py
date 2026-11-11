"""Módulo Habitaciones - Modelos.

Integrante 1: modelo Habitación, CRUD, tipos de habitación, fotografías
y registro en el panel administrativo.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

# Estados de reservación que ocupan la habitación
ESTADOS_ACTIVOS = ['Pendiente', 'Confirmada']


class Habitacion(models.Model):
    """Habitación del hotel Paradise."""

    TIPOS = [
        ('Individual', 'Individual'),
        ('Doble', 'Doble'),
        ('Suite', 'Suite'),
        ('Presidencial', 'Presidencial'),
    ]

    numero = models.PositiveIntegerField(
        'Número',
        unique=True,
        validators=[MinValueValidator(1)],
        help_text='Número de habitación (no se puede repetir).',
    )
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS, default='Individual')
    precio_noche = models.DecimalField(
        'Precio por noche',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    capacidad = models.PositiveIntegerField(
        'Capacidad',
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Número de personas que pueden hospedarse.',
    )
    disponible = models.BooleanField('Disponible', default=True)
    imagen = models.ImageField(
        'Imagen',
        upload_to='habitaciones/',
        blank=True,
        null=True,
        help_text='Fotografía opcional de la habitación.',
    )
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'
        ordering = ['numero']

    def __str__(self):
        return f'Habitación {self.numero} - {self.tipo}'

    def get_absolute_url(self):
        return reverse('habitaciones:detalle', args=[self.pk])

    def reservaciones_activas(self):
        """Reservaciones que todavía ocupan la habitación (no canceladas)."""
        return self.reservaciones.filter(
            estado__in=ESTADOS_ACTIVOS,
            fecha_salida__gte=timezone.localdate(),
        )

    def tiene_reservaciones_activas(self):
        return self.reservaciones_activas().exists()

    def esta_disponible_en(self, fecha_entrada, fecha_salida, excluir_pk=None):
        """Regresa True si la habitación está libre en ese rango de fechas."""
        if not self.disponible:
            return False
        choques = self.reservaciones.filter(
            estado__in=ESTADOS_ACTIVOS,
            fecha_entrada__lt=fecha_salida,
            fecha_salida__gt=fecha_entrada,
        )
        if excluir_pk:
            choques = choques.exclude(pk=excluir_pk)
        return not choques.exists()
