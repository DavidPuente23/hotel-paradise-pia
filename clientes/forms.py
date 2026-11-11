"""Formularios del módulo Clientes."""

from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes."""

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellidos', 'correo', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        qs = Cliente.objects.filter(correo__iexact=correo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un cliente registrado con ese correo.')
        return correo

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono'].strip()
        if len(telefono) < 7:
            raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos.')
        return telefono
