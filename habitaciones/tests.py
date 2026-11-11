"""Pruebas funcionales del módulo Habitaciones."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from reservaciones.models import Reservacion

from .forms import HabitacionForm
from .models import Habitacion


class HabitacionModelTests(TestCase):
    def setUp(self):
        self.habitacion = Habitacion.objects.create(
            numero=101, tipo='Doble', precio_noche=Decimal('1000.00'), capacidad=2
        )

    def test_numero_repetido_no_es_valido(self):
        """Regla 3: no se pueden registrar números de habitación repetidos."""
        form = HabitacionForm(data={
            'numero': 101, 'tipo': 'Individual', 'precio_noche': '800',
            'capacidad': 1, 'disponible': True,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('numero', form.errors)

    def test_precio_debe_ser_positivo(self):
        form = HabitacionForm(data={
            'numero': 102, 'tipo': 'Individual', 'precio_noche': '0',
            'capacidad': 1, 'disponible': True,
        })
        self.assertFalse(form.is_valid())


class EliminarHabitacionTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('empleado', password='clave12345')
        self.client.force_login(self.usuario)

        self.cliente = Cliente.objects.create(
            nombre='Ana', apellidos='López', correo='ana@example.com', telefono='8112345678'
        )
        self.habitacion = Habitacion.objects.create(
            numero=201, tipo='Suite', precio_noche=Decimal('2500.00'), capacidad=4
        )
        self.hoy = timezone.localdate()
        self.reservacion = Reservacion.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_entrada=self.hoy,
            fecha_salida=self.hoy + timedelta(days=2),
            estado='Confirmada',
        )

    def test_no_elimina_habitacion_con_reservacion_activa(self):
        """Regla 5: no se puede eliminar una habitación con reservaciones activas."""
        respuesta = self.client.post(reverse('habitaciones:eliminar', args=[self.habitacion.pk]))
        self.assertRedirects(respuesta, reverse('habitaciones:detalle', args=[self.habitacion.pk]))
        self.assertTrue(Habitacion.objects.filter(pk=self.habitacion.pk).exists())

    def test_elimina_habitacion_sin_reservaciones(self):
        libre = Habitacion.objects.create(
            numero=202, tipo='Doble', precio_noche=Decimal('1500.00'), capacidad=2
        )
        respuesta = self.client.post(reverse('habitaciones:eliminar', args=[libre.pk]))
        self.assertRedirects(respuesta, reverse('habitaciones:lista'))
        self.assertFalse(Habitacion.objects.filter(pk=libre.pk).exists())

    def test_listado_requiere_iniciar_sesion(self):
        self.client.logout()
        respuesta = self.client.get(reverse('habitaciones:lista'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('cuentas:login'), respuesta.url)
