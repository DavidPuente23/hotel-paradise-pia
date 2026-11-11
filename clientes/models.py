"""Módulo Clientes - Modelos.

Integrante 2: modelo Cliente, CRUD, validación de correo y búsquedas.
"""

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse


class Cliente(models.Model):
    """Cliente registrado en el hotel."""

    nombre = models.CharField('Nombre', max_length=80)
    apellidos = models.CharField('Apellidos', max_length=120)
    correo = models.EmailField(
        'Correo electrónico',
        max_length=150,
        unique=True,
        help_text='El correo debe ser único.',
    )
    telefono = models.CharField(
        'Teléfono',
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[0-9+\-\s()]{7,20}$',
                message='Escribe un teléfono válido (solo números, +, - y espacios).',
            )
        ],
    )
    fecha_registro = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellidos', 'nombre']

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'

    def get_absolute_url(self):
        return reverse('clientes:detalle', args=[self.pk])

    def save(self, *args, **kwargs):
        # Guardamos el correo siempre en minúsculas para evitar duplicados
        self.correo = self.correo.strip().lower()
        self.nombre = self.nombre.strip().title()
        self.apellidos = self.apellidos.strip().title()
        super().save(*args, **kwargs)
