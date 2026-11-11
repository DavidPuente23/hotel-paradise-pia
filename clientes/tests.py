"""Pruebas funcionales del módulo Clientes."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ClienteForm
from .models import Cliente


class ClienteFormTests(TestCase):
    def test_correo_duplicado_no_es_valido(self):
        """Regla 4: el correo del cliente debe ser único."""
        Cliente.objects.create(
            nombre='Ana', apellidos='López', correo='ana@example.com', telefono='8112345678'
        )
        form = ClienteForm(data={
            'nombre': 'Otra', 'apellidos': 'Persona',
            'correo': 'ANA@example.com', 'telefono': '8199999999',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)

    def test_correo_invalido_no_es_valido(self):
        form = ClienteForm(data={
            'nombre': 'Luis', 'apellidos': 'Pérez',
            'correo': 'correo-invalido', 'telefono': '8112345678',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)

    def test_telefono_muy_corto_no_es_valido(self):
        form = ClienteForm(data={
            'nombre': 'Luis', 'apellidos': 'Pérez',
            'correo': 'luis@example.com', 'telefono': '123',
        })
        self.assertFalse(form.is_valid())


class BusquedaClienteTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('empleado', password='clave12345')
        self.client.force_login(self.usuario)
        Cliente.objects.create(
            nombre='María', apellidos='Torres', correo='maria@example.com', telefono='8111111111'
        )
        Cliente.objects.create(
            nombre='Carlos', apellidos='Ramírez', correo='carlos@example.com', telefono='8122222222'
        )

    def test_busqueda_por_nombre(self):
        respuesta = self.client.get(reverse('clientes:lista'), {'q': 'María'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'maria@example.com')
        self.assertNotContains(respuesta, 'carlos@example.com')

    def test_busqueda_por_correo(self):
        respuesta = self.client.get(reverse('clientes:lista'), {'q': 'carlos@'})
        self.assertContains(respuesta, 'Carlos')
        self.assertNotContains(respuesta, 'María')
