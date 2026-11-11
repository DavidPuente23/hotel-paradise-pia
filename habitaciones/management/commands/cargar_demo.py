"""Comando para cargar datos de demostración.

Uso:
    python manage.py cargar_demo
"""

from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from clientes.models import Cliente
from habitaciones.models import Habitacion
from reservaciones.models import Reservacion

HABITACIONES = [
    (101, 'Individual', 850, 1, 'Habitación cómoda con cama individual y escritorio.'),
    (102, 'Individual', 850, 1, 'Habitación individual con vista al jardín.'),
    (103, 'Doble', 1450, 2, 'Habitación con dos camas matrimoniales y balcón.'),
    (104, 'Doble', 1450, 2, 'Habitación doble con televisión de 50 pulgadas.'),
    (105, 'Doble', 1450, 2, 'Habitación doble familiar con sofá.'),
    (201, 'Suite', 2900, 4, 'Suite con sala, cocineta y jacuzzi.'),
    (202, 'Suite', 2900, 4, 'Suite con terraza y vista a la alberca.'),
    (203, 'Suite', 2900, 4, 'Suite ejecutiva con área de trabajo.'),
    (301, 'Presidencial', 6500, 6, 'Suite presidencial con comedor y dos recámaras.'),
    (302, 'Presidencial', 6500, 6, 'Suite presidencial con alberca privada.'),
]

CLIENTES = [
    ('Ana', 'López García', 'ana.lopez@example.com', '8112345678'),
    ('Carlos', 'Ramírez Soto', 'carlos.ramirez@example.com', '8187654321'),
    ('María Fernanda', 'Torres Ruiz', 'maria.torres@example.com', '8123456789'),
    ('José Luis', 'Hernández Cruz', 'jose.hernandez@example.com', '8198765432'),
    ('Sofía', 'Martínez Flores', 'sofia.martinez@example.com', '8145678901'),
    ('Roberto', 'Díaz Peña', 'roberto.diaz@example.com', '8111223344'),
]


class Command(BaseCommand):
    help = 'Carga habitaciones, clientes y reservaciones de demostración.'

    def handle(self, *args, **options):
        self.crear_administrador()
        self.crear_habitaciones()
        self.crear_clientes()
        self.crear_reservaciones()
        self.stdout.write(self.style.SUCCESS('Datos de demostración cargados correctamente.'))

    def crear_administrador(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@hotelparadise.com',
                password='hotel1234',
                first_name='David',
                last_name='Puente',
            )
            self.stdout.write('Usuario administrador creado: admin / hotel1234')
        else:
            self.stdout.write('El usuario admin ya existe.')

    def crear_habitaciones(self):
        if Habitacion.objects.exists():
            self.stdout.write('Ya existen habitaciones; no se volvieron a crear.')
            return
        for numero, tipo, precio, capacidad, descripcion in HABITACIONES:
            habitacion = Habitacion(
                numero=numero,
                tipo=tipo,
                precio_noche=Decimal(str(precio)),
                capacidad=capacidad,
                descripcion=descripcion,
                disponible=True,
            )
            imagen = self.generar_imagen(numero, tipo)
            if imagen:
                habitacion.imagen.save(f'habitacion_{numero}.jpg', imagen, save=False)
            habitacion.save()
        self.stdout.write(f'Se crearon {len(HABITACIONES)} habitaciones.')

    def generar_imagen(self, numero, tipo):
        """Genera una ilustración sencilla para demostrar el campo ImageField."""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return None

        # Paleta de colores por tipo de habitación
        paletas = {
            'Individual': ((238, 231, 219), (196, 148, 92), (56, 92, 120)),
            'Doble': ((224, 236, 228), (150, 178, 138), (56, 92, 70)),
            'Suite': ((240, 231, 212), (206, 168, 100), (110, 78, 40)),
            'Presidencial': ((233, 224, 238), (150, 120, 160), (78, 52, 88)),
        }
        pared, acento, oscuro = paletas.get(tipo, ((232, 232, 232), (180, 180, 180), (70, 70, 70)))

        imagen = Image.new('RGB', (800, 500), pared)
        d = ImageDraw.Draw(imagen)

        # Piso
        d.rectangle([0, 350, 800, 500], fill=(176, 138, 100))
        for x in range(0, 800, 80):
            d.line([(x, 350), (x, 500)], fill=(160, 124, 88), width=2)
        d.line([(0, 350), (800, 350)], fill=(140, 105, 72), width=6)

        # Ventana con vista al cielo
        d.rectangle([520, 70, 740, 280], fill=(178, 214, 238))
        d.rectangle([520, 70, 740, 280], outline=(250, 250, 250), width=10)
        d.line([(630, 70), (630, 280)], fill=(250, 250, 250), width=8)
        d.line([(520, 175), (740, 175)], fill=(250, 250, 250), width=8)
        d.ellipse([660, 100, 700, 140], fill=(255, 232, 160))

        # Cama: cabecero, colchón, almohadas y cobija
        d.rounded_rectangle([60, 210, 420, 330], radius=10, fill=oscuro)
        d.rounded_rectangle([70, 300, 440, 400], radius=16, fill=(252, 250, 245))
        d.rounded_rectangle([240, 300, 440, 400], radius=16, fill=acento)
        d.rounded_rectangle([90, 250, 210, 305], radius=14, fill=(255, 255, 255))
        d.rounded_rectangle([225, 250, 345, 305], radius=14, fill=(255, 255, 255))
        d.rectangle([60, 400, 90, 460], fill=oscuro)
        d.rectangle([410, 400, 440, 460], fill=oscuro)

        # Buró y lámpara
        d.rectangle([470, 330, 560, 420], fill=oscuro)
        d.ellipse([495, 285, 545, 335], fill=(255, 236, 180))
        d.rectangle([515, 320, 525, 335], fill=oscuro)

        # Tapete
        d.ellipse([140, 410, 480, 465], fill=(214, 190, 160))

        archivo = BytesIO()
        imagen.save(archivo, format='JPEG', quality=88)
        return ContentFile(archivo.getvalue())

    def crear_clientes(self):
        if Cliente.objects.exists():
            self.stdout.write('Ya existen clientes; no se volvieron a crear.')
            return
        for nombre, apellidos, correo, telefono in CLIENTES:
            Cliente.objects.create(nombre=nombre, apellidos=apellidos, correo=correo, telefono=telefono)
        self.stdout.write(f'Se crearon {len(CLIENTES)} clientes.')

    def crear_reservaciones(self):
        if Reservacion.objects.exists():
            self.stdout.write('Ya existen reservaciones; no se volvieron a crear.')
            return

        hoy = timezone.localdate()
        room = {h.numero: h for h in Habitacion.objects.all()}
        cliente = {c.nombre: c for c in Cliente.objects.all()}

        datos = [
            (cliente['Ana'], room[101], hoy - timedelta(days=5), hoy - timedelta(days=2), 'Finalizada'),
            (cliente['Carlos'], room[201], hoy - timedelta(days=3), hoy + timedelta(days=2), 'Confirmada'),
            (cliente['María Fernanda'], room[103], hoy, hoy + timedelta(days=3), 'Confirmada'),
            (cliente['José Luis'], room[301], hoy + timedelta(days=5), hoy + timedelta(days=8), 'Pendiente'),
            (cliente['Sofía'], room[104], hoy - timedelta(days=10), hoy - timedelta(days=7), 'Finalizada'),
            (cliente['Roberto'], room[202], hoy + timedelta(days=2), hoy + timedelta(days=6), 'Pendiente'),
            (cliente['Ana'], room[102], hoy + timedelta(days=10), hoy + timedelta(days=12), 'Cancelada'),
            (cliente['Carlos'], room[105], hoy + timedelta(days=1), hoy + timedelta(days=4), 'Confirmada'),
            (cliente['María Fernanda'], room[203], hoy - timedelta(days=1), hoy + timedelta(days=1), 'Confirmada'),
            (cliente['José Luis'], room[302], hoy + timedelta(days=15), hoy + timedelta(days=18), 'Pendiente'),
        ]

        for cli, hab, entrada, salida, estado in datos:
            Reservacion.objects.create(
                cliente=cli,
                habitacion=hab,
                fecha_entrada=entrada,
                fecha_salida=salida,
                estado=estado,
            )
        self.stdout.write(f'Se crearon {len(datos)} reservaciones.')
