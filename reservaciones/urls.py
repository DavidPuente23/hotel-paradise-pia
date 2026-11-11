"""Rutas del módulo Reservaciones."""

from django.urls import path

from . import views

app_name = 'reservaciones'

urlpatterns = [
    path('', views.lista_reservaciones, name='lista'),
    path('nueva/', views.crear_reservacion, name='crear'),
    path('disponibilidad/', views.consultar_disponibilidad, name='disponibilidad'),
    path('<int:pk>/', views.detalle_reservacion, name='detalle'),
    path('<int:pk>/editar/', views.editar_reservacion, name='editar'),
    path('<int:pk>/cancelar/', views.cancelar_reservacion, name='cancelar'),
]
