"""Formularios de seguridad y control de usuarios."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión con estilos de Bootstrap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Usuario'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})


class UsuarioForm(UserCreationForm):
    """Formulario para que el administrador cree usuarios del sistema."""

    is_staff = forms.BooleanField(
        label='¿Es administrador?',
        required=False,
        help_text='Los administradores pueden entrar al panel de Django y administrar usuarios.',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs.update({'class': 'form-check-input'})
            else:
                campo.widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = 'Obligatorio. Máximo 150 caracteres.'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres, no puede ser una contraseña común.'
        self.fields['password2'].help_text = 'Escribe la misma contraseña para confirmar.'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario con ese correo.')
        return email
