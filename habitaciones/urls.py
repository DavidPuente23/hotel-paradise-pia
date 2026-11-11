"""Rutas del módulo Habitaciones."""

from django.urls import path

from . import views

app_name = 'habitaciones'

urlpatterns = [
    path('', views.lista_habitaciones, name='lista'),
    path('nueva/', views.crear_habitacion, name='crear'),
    path('tipos/', views.tipos_habitacion, name='tipos'),
    path('<int:pk>/', views.detalle_habitacion, name='detalle'),
    path('<int:pk>/editar/', views.editar_habitacion, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_habitacion, name='eliminar'),
]
