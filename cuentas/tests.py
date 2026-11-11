"""Pruebas del módulo Seguridad y Reportes."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccesoSeguridadTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            'admin', password='hotel1234', is_staff=True
        )
        self.empleado = User.objects.create_user('empleado', password='clave12345')

    def test_dashboard_sin_sesion_redirige_al_login(self):
        """Un visitante anónimo no puede entrar al dashboard."""
        respuesta = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(
            respuesta,
            f"{reverse('cuentas:login')}?next={reverse('core:dashboard')}",
        )

    def test_reportes_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(reverse('core:reportes'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('cuentas:login'), respuesta['Location'])

    def test_lista_usuarios_solo_para_administradores(self):
        """Un empleado normal es enviado al login, no ve la lista de usuarios."""
        self.client.force_login(self.empleado)
        respuesta = self.client.get(reverse('cuentas:usuarios'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('cuentas:login'), respuesta['Location'])

    def test_administrador_puede_ver_usuarios(self):
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('cuentas:usuarios'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'empleado')

    def test_login_valido_entra_al_dashboard(self):
        respuesta = self.client.post(
            reverse('cuentas:login'),
            {'username': 'admin', 'password': 'hotel1234'},
        )
        self.assertRedirects(respuesta, reverse('core:dashboard'))

    def test_login_invalido_muestra_error(self):
        respuesta = self.client.post(
            reverse('cuentas:login'),
            {'username': 'admin', 'password': 'incorrecta'},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'incorrectos')


class ControlUsuariosTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            'admin', password='hotel1234', is_staff=True
        )
        self.otro = User.objects.create_user('recepcion', password='clave12345')
        self.client.force_login(self.admin)

    def test_administrador_no_puede_desactivarse_a_si_mismo(self):
        respuesta = self.client.post(
            reverse('cuentas:cambiar_estado', args=[self.admin.pk])
        )
        self.assertRedirects(respuesta, reverse('cuentas:usuarios'))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_administrador_desactiva_a_otro_usuario(self):
        respuesta = self.client.post(
            reverse('cuentas:cambiar_estado', args=[self.otro.pk])
        )
        self.assertRedirects(respuesta, reverse('cuentas:usuarios'))
        self.otro.refresh_from_db()
        self.assertFalse(self.otro.is_active)

    def test_cambiar_estado_requiere_post(self):
        """No se puede desactivar un usuario con un simple enlace GET."""
        respuesta = self.client.get(
            reverse('cuentas:cambiar_estado', args=[self.otro.pk])
        )
        self.assertEqual(respuesta.status_code, 405)
        self.otro.refresh_from_db()
        self.assertTrue(self.otro.is_active)
