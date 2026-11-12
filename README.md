# Hotel Paradise - Sistema de Reservación de Hotel

Proyecto Final de **Fundamentos de Desarrollo Web** desarrollado con Django 5 y Bootstrap 5.

**Alumno:** David Alejandro Puente Muñiz
**Matrícula:** 2179996
**Repositorio:** <https://github.com/DavidPuente23/hotel-paradise-pia>

---

## Descripción

Aplicación web para administrar las habitaciones, los clientes y las reservaciones de la cadena
hotelera **Hotel Paradise**. Incluye autenticación, CRUD completo, validación automática de
disponibilidad, dashboard con estadísticas y reportes.

## Funcionalidades principales

- **Habitaciones:** alta, consulta, edición y eliminación; tipos de habitación, precios,
  capacidad, disponibilidad y fotografía.
- **Clientes:** alta, consulta, edición y eliminación; validación y unicidad del correo;
  búsqueda por nombre, correo o teléfono.
- **Reservaciones:** registro, consulta, modificación y cancelación; cálculo automático del
  total; validación de fechas y de disponibilidad de la habitación.
- **Disponibilidad:** consulta de habitaciones libres por rango de fechas, tipo y capacidad.
- **Dashboard:** total de clientes, habitaciones, reservaciones, habitaciones disponibles,
  ingresos generados y porcentaje de ocupación del día.
- **Reportes:** reservaciones por estado y por tipo, ingresos por mes, top de clientes,
  habitaciones más reservadas y exportación a CSV.
- **Seguridad:** login, logout, cambio de contraseña y control de usuarios (solo administradores).
- **Panel de administración de Django** con los tres modelos registrados.

## Tecnologías

| Tecnología | Uso |
| --- | --- |
| Python 3.11 | Lenguaje de programación |
| Django 5.2 | Framework web (MTV) |
| SQLite | Base de datos |
| Bootstrap 5.3 | Interfaz sencilla y responsiva |
| Pillow | Procesamiento de imágenes |
| HTML / CSS / JavaScript | Templates y cálculo visual del total |

## Instalación y ejecución

1. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Crear la base de datos y aplicar las migraciones:

   ```bash
   python manage.py migrate
   ```

3. Cargar los datos de demostración (crea el usuario administrador, 10 habitaciones,
   6 clientes y 10 reservaciones):

   ```bash
   python manage.py cargar_demo
   ```

4. Iniciar el servidor:

   ```bash
   python manage.py runserver
   ```

5. Abrir <http://127.0.0.1:8000/> en el navegador.

### Usuario de prueba

| Usuario | Contraseña | Rol |
| --- | --- | --- |
| `admin` | `hotel1234` | Administrador |

También se puede crear un superusuario propio con `python manage.py createsuperuser`.

## Pruebas

El proyecto incluye 28 pruebas funcionales (modelos, formularios, reglas de negocio,
vistas y seguridad):

```bash
python manage.py test
```

## Estructura del proyecto

```
hotel_paradise/
├── config/                 # Configuración general (settings, urls, wsgi)
├── core/                   # Dashboard, reportes y exportación CSV
├── habitaciones/           # Modelo, formularios, vistas y admin de habitaciones
├── clientes/               # Modelo, formularios, vistas y admin de clientes
├── reservaciones/          # Modelo, formularios, vistas, disponibilidad y cancelación
├── cuentas/                # Login, logout, cambio de contraseña y control de usuarios
├── templates/              # Templates generales y de cada módulo
├── static/css/             # Hoja de estilos propia
├── media/                  # Fotografías subidas de las habitaciones
├── docs/                   # Documento técnico, manual de usuario y capturas
├── manage.py
└── requirements.txt
```

## Rutas principales

| Ruta | Descripción |
| --- | --- |
| `/` | Dashboard |
| `/habitaciones/` | CRUD de habitaciones |
| `/habitaciones/tipos/` | Resumen de tipos de habitación |
| `/clientes/` | CRUD de clientes |
| `/reservaciones/` | CRUD de reservaciones |
| `/reservaciones/disponibilidad/` | Consulta de disponibilidad |
| `/reportes/` | Reportes y estadísticas |
| `/cuentas/login/` | Inicio de sesión |
| `/cuentas/usuarios/` | Control de usuarios (solo administradores) |
| `/admin/` | Panel de administración de Django |

## Reglas de negocio implementadas

1. Una habitación no se puede reservar dos veces en las mismas fechas.
2. La fecha de salida debe ser mayor que la fecha de entrada.
3. No se pueden registrar números de habitación repetidos.
4. El correo del cliente debe ser único.
5. No se puede eliminar una habitación con reservaciones activas.

Las reglas 1 y 2 están en `reservaciones/models.py` (`Reservacion.clean`) y en
`reservaciones/forms.py`; la regla 3 en el modelo `Habitacion` (campo `unique=True`);
la regla 4 en el modelo `Cliente` y en `ClienteForm.clean_correo`; y la regla 5 en
`habitaciones/views.py` (vista `eliminar_habitacion`).

## Documentación

- [Documento técnico](docs/DOCUMENTO_TECNICO.md)
- [Manual de usuario](docs/MANUAL_USUARIO.md)
- [Guion para el video de presentación](docs/GUION_VIDEO.md)
- Versiones en Word: `docs/Documento_Tecnico.docx` y `docs/Manual_de_Usuario.docx`
