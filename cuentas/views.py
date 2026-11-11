"""Módulo Seguridad y Reportes - Vistas.

Integrante 5: login, logout, control de usuarios.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import LoginForm, UsuarioForm


class IniciarSesionView(LoginView):
    """Pantalla de inicio de sesión."""

    template_name = 'cuentas/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class CerrarSesionView(LogoutView):
    """Cierra la sesión del usuario."""

    next_page = reverse_lazy('cuentas:login')


class CambiarPasswordView(PasswordChangeView):
    """Permite al usuario cambiar su contraseña."""

    template_name = 'cuentas/cambiar_password.html'
    success_url = reverse_lazy('core:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Tu contraseña se actualizó correctamente.')
        return super().form_valid(form)


def es_administrador(usuario):
    return usuario.is_authenticated and usuario.is_staff


@user_passes_test(es_administrador, login_url='cuentas:login')
def lista_usuarios(request):
    """Lista de usuarios del sistema (solo administradores)."""
    usuarios = User.objects.all().order_by('username')
    return render(request, 'cuentas/usuarios_lista.html', {'usuarios': usuarios})


@user_passes_test(es_administrador, login_url='cuentas:login')
def crear_usuario(request):
    """Alta de usuarios del sistema (solo administradores)."""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.username}" creado correctamente.')
            return redirect('cuentas:usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'cuentas/usuario_form.html', {'form': form})


@require_POST
@user_passes_test(es_administrador, login_url='cuentas:login')
def cambiar_estado_usuario(request, pk):
    """Activa o desactiva un usuario (no permite desactivarse a sí mismo)."""
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario.')
        return redirect('cuentas:usuarios')

    usuario.is_active = not usuario.is_active
    usuario.save()
    estado = 'activado' if usuario.is_active else 'desactivado'
    messages.success(request, f'El usuario "{usuario.username}" fue {estado}.')
    return redirect('cuentas:usuarios')
