"""Rutas del dashboard y reportes."""

from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/exportar/', views.exportar_reservaciones_csv, name='exportar_csv'),
]
