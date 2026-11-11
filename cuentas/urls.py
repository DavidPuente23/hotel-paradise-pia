"""Rutas del módulo de seguridad."""

from django.urls import path

from . import views

app_name = 'cuentas'

urlpatterns = [
    path('login/', views.IniciarSesionView.as_view(), name='login'),
    path('logout/', views.CerrarSesionView.as_view(), name='logout'),
    path('password/', views.CambiarPasswordView.as_view(), name='cambiar_password'),
    path('usuarios/', views.lista_usuarios, name='usuarios'),
    path('usuarios/nuevo/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/estado/', views.cambiar_estado_usuario, name='cambiar_estado'),
]
