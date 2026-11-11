"""Formularios del módulo Reservaciones."""

from datetime import date

from django import forms

from habitaciones.models import Habitacion
from .models import Reservacion


class ReservacionForm(forms.ModelForm):
    """Formulario para registrar y modificar reservaciones.

    Las validaciones de fechas y disponibilidad están en Reservacion.clean().
    """

    class Meta:
        model = Reservacion
        fields = ['cliente', 'habitacion', 'fecha_entrada', 'fecha_salida', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'habitacion': forms.Select(attrs={'class': 'form-select'}),
            'fecha_entrada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_salida': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        datos = super().clean()
        entrada = datos.get('fecha_entrada')
        salida = datos.get('fecha_salida')

        # Regla 2 (validación amigable en el formulario)
        if entrada and salida and salida <= entrada:
            self.add_error('fecha_salida', 'La fecha de salida debe ser mayor que la fecha de entrada.')

        # Sugerencia: no permitir reservar fechas ya pasadas
        if entrada and entrada < date.today() and not self.instance.pk:
            self.add_error('fecha_entrada', 'La fecha de entrada no puede ser anterior a hoy.')

        return datos


class DisponibilidadForm(forms.Form):
    """Formulario para consultar habitaciones disponibles."""

    fecha_entrada = forms.DateField(
        label='Fecha de entrada',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    fecha_salida = forms.DateField(
        label='Fecha de salida',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    tipo = forms.ChoiceField(
        label='Tipo de habitación',
        required=False,
        choices=[('', 'Todos los tipos')] + Habitacion.TIPOS,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    capacidad = forms.IntegerField(
        label='Capacidad mínima',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Ej. 2'}),
    )

    def clean(self):
        datos = super().clean()
        entrada = datos.get('fecha_entrada')
        salida = datos.get('fecha_salida')
        if entrada and salida:
            if salida <= entrada:
                self.add_error('fecha_salida', 'La fecha de salida debe ser mayor que la fecha de entrada.')
            elif entrada < date.today():
                self.add_error('fecha_entrada', 'La fecha de entrada no puede ser anterior a hoy.')
        return datos
