"""Formularios del módulo Habitaciones."""

from django import forms

from .models import Habitacion


class HabitacionForm(forms.ModelForm):
    """Formulario para crear y editar habitaciones."""

    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'precio_noche', 'capacidad', 'disponible', 'imagen', 'descripcion']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'precio_noche': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_numero(self):
        numero = self.cleaned_data['numero']
        if numero <= 0:
            raise forms.ValidationError('El número de habitación debe ser mayor que cero.')
        return numero

    def clean_precio_noche(self):
        precio = self.cleaned_data['precio_noche']
        if precio <= 0:
            raise forms.ValidationError('El precio por noche debe ser mayor que cero.')
        return precio

    def clean_capacidad(self):
        capacidad = self.cleaned_data['capacidad']
        if capacidad <= 0:
            raise forms.ValidationError('La capacidad debe ser al menos de 1 persona.')
        return capacidad
