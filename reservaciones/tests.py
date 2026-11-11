"""Pruebas funcionales del módulo Reservaciones."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from habitaciones.models import Habitacion

from .forms import ReservacionForm
from .models import Reservacion


class ReservacionValidacionesTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.cliente = Cliente.objects.create(
            nombre='Ana', apellidos='López', correo='ana@example.com', telefono='8112345678'
        )
        self.habitacion = Habitacion.objects.create(
            numero=101, tipo='Doble', precio_noche=Decimal('1000.00'), capacidad=2
        )

    def test_fecha_salida_debe_ser_mayor(self):
        """Regla 2: la fecha de salida debe ser mayor que la entrada."""
        form = ReservacionForm(data={
            'cliente': self.cliente.pk,
            'habitacion': self.habitacion.pk,
            'fecha_entrada': self.hoy + timedelta(days=5),
            'fecha_salida': self.hoy + timedelta(days=5),
            'estado': 'Pendiente',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_salida', form.errors)

    def test_no_permite_reservaciones_encimadas(self):
        """Regla 1: una habitación no se reserva dos veces en las mismas fechas."""
        Reservacion.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_entrada=self.hoy + timedelta(days=2),
            fecha_salida=self.hoy + timedelta(days=5),
            estado='Confirmada',
        )
        form = ReservacionForm(data={
            'cliente': self.cliente.pk,
            'habitacion': self.habitacion.pk,
            'fecha_entrada': self.hoy + timedelta(days=3),
            'fecha_salida': self.hoy + timedelta(days=6),
            'estado': 'Pendiente',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('habitacion', form.errors)

    def test_permite_fechas_continuas(self):
        """Salir el mismo día en que entra otro cliente sí es válido."""
        Reservacion.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_entrada=self.hoy + timedelta(days=2),
            fecha_salida=self.hoy + timedelta(days=5),
            estado='Confirmada',
        )
        form = ReservacionForm(data={
            'cliente': self.cliente.pk,
            'habitacion': self.habitacion.pk,
            'fecha_entrada': self.hoy + timedelta(days=5),
            'fecha_salida': self.hoy + timedelta(days=7),
            'estado': 'Pendiente',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_total_se_calcula_automaticamente(self):
        reservacion = Reservacion.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_entrada=self.hoy + timedelta(days=1),
            fecha_salida=self.hoy + timedelta(days=4),
            estado='Pendiente',
        )
        # 3 noches x $1000
        self.assertEqual(reservacion.total, Decimal('3000.00'))
        self.assertEqual(reservacion.noches, 3)

    def test_reservacion_cancelada_no_bloquea_fechas(self):
        Reservacion.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_entrada=self.hoy + timedelta(days=2),
            fecha_salida=self.hoy + timedelta(days=5),
            estado='Cancelada',
        )
        form = ReservacionForm(data={
            'cliente': self.cliente.pk,
            'habitacion': self.habitacion.pk,
            'fecha_entrada': self.hoy + timedelta(days=2),
            'fecha_salida': self.hoy + timedelta(days=5),
            'estado': 'Pendiente',
        })
        self.assertTrue(form.is_valid(), form.errors)


class ReservacionVistasTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('empleado', password='clave12345')
        self.client.force_login(self.usuario)
        self.hoy = timezone.localdate()
        self.cliente = Cliente.objects.create(
            nombre='Ana', apellidos='López', correo='ana@example.com', telefono='8112345678'
        )
        self.habitacion = Habitacion.objects.create(
            numero=101, tipo='Doble', precio_noche=Decimal('1000.00'), capacidad=2
        )

    def test_cancelar_reservacion(self):
        reservacion = Reservacion.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_entrada=self.hoy + timedelta(days=1),
            fecha_salida=self.hoy + timedelta(days=3),
            estado='Confirmada',
        )
        respuesta = self.client.post(reverse('reservaciones:cancelar', args=[reservacion.pk]))
        self.assertRedirects(respuesta, reverse('reservaciones:detalle', args=[reservacion.pk]))
        reservacion.refresh_from_db()
        self.assertEqual(reservacion.estado, 'Cancelada')

    def test_disponibilidad_muestra_solo_habitaciones_libres(self):
        libre = Habitacion.objects.create(
            numero=102, tipo='Individual', precio_noche=Decimal('800.00'), capacidad=1
        )
        Reservacion.objects.create(
            cliente=self.cliente,
            habitacion=self.habitacion,
            fecha_entrada=self.hoy + timedelta(days=2),
            fecha_salida=self.hoy + timedelta(days=5),
            estado='Confirmada',
        )
        respuesta = self.client.get(reverse('reservaciones:disponibilidad'), {
            'fecha_entrada': (self.hoy + timedelta(days=3)).isoformat(),
            'fecha_salida': (self.hoy + timedelta(days=4)).isoformat(),
        })
        self.assertEqual(respuesta.status_code, 200)
        habitaciones = [fila['habitacion'] for fila in respuesta.context['resultados']]
        self.assertIn(libre, habitaciones)
        self.assertNotIn(self.habitacion, habitaciones)


class DashboardTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('empleado', password='clave12345')

    def test_dashboard_requiere_sesion(self):
        respuesta = self.client.get(reverse('core:dashboard'))
        self.assertEqual(respuesta.status_code, 302)

    def test_dashboard_muestra_estadisticas(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse('core:dashboard'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('total_clientes', respuesta.context)
        self.assertIn('ingresos', respuesta.context)
