# Guion para el video de presentación (5 minutos)

**Proyecto:** Sistema de Reservación de Hotel "Hotel Paradise"  
**Alumno:** David Alejandro Puente Muñiz - 2179996

> Consejo: grabar la pantalla con el sistema ya iniciado y los datos de demostración cargados.
> Hablar de forma tranquila y mostrar lo que se menciona.

---

## 0:00 - 0:30 | Presentación

"Hola, mi nombre es David Alejandro Puente Muñiz, matrícula 2179996, y presento el proyecto final
de Fundamentos de Desarrollo Web: el Sistema de Reservación de Hotel Hotel Paradise, desarrollado
con Django, SQLite y Bootstrap 5."

Mostrar la pantalla de login.

## 0:30 - 1:00 | Inicio de sesión y dashboard

"El sistema cuenta con autenticación. Inicio sesión con el usuario administrador y accedo al
dashboard, donde se muestran los indicadores principales: total de clientes, habitaciones,
reservaciones, habitaciones disponibles, ingresos generados y el porcentaje de ocupación del día.
También se muestran las últimas reservaciones y las próximas llegadas."

Iniciar sesión y recorrer el dashboard.

## 1:00 - 1:50 | Módulo Habitaciones

"El módulo de habitaciones incluye el CRUD completo. Puedo buscar por número o tipo, filtrar por
disponibilidad y ver la fotografía de cada habitación. Al crear una habitación, el sistema valida
que el número no se repita y que el precio y la capacidad sean mayores que cero."

Mostrar el listado y abrir el formulario de nueva habitación. Intentar guardar un número repetido
para mostrar la validación.

"También puedo editar y eliminar. Si la habitación tiene reservaciones activas, el sistema impide
eliminarla, cumpliendo la regla de negocio número 5."

Mostrar el aviso de eliminación.

## 1:50 - 2:30 | Módulo Clientes

"El módulo de clientes permite registrar, consultar, modificar y eliminar clientes. El correo es
único y se valida su formato; el teléfono también se valida. La búsqueda se puede hacer por
nombre, correo o teléfono. Al abrir un cliente se muestra su historial de reservaciones."

Mostrar listado, búsqueda y ficha del cliente.

## 2:30 - 3:40 | Módulo Reservaciones y disponibilidad

"El módulo de reservaciones es el corazón del sistema. Primero consulto la disponibilidad:
selecciono las fechas y el sistema muestra solo las habitaciones libres, con el total estimado."

Mostrar la consulta de disponibilidad.

"Al reservar, el sistema valida que la fecha de salida sea mayor que la entrada, que la habitación
no esté ocupada en esas fechas y que no esté marcada como no disponible. El total se calcula
automáticamente multiplicando las noches por el precio."

Mostrar el formulario con el total estimado y provocar un error de disponibilidad.

"También puedo modificar una reservación o cancelarla; al cancelarla, las fechas quedan libres
pero se conserva el historial."

## 3:40 - 4:25 | Interfaz, reportes y seguridad

"La interfaz está construida con Bootstrap 5, con un menú de navegación, diseño responsivo,
mensajes de confirmación y un template base reutilizable. El módulo de reportes usa consultas
avanzadas del ORM para mostrar reservaciones por estado, por tipo de habitación, ingresos por mes,
los mejores clientes y las habitaciones más reservadas. También permite exportar a CSV."

Mostrar reportes y descargar el CSV.

"En seguridad, el sistema tiene login, logout, cambio de contraseña y control de usuarios. Solo
los administradores pueden crear o desactivar cuentas. Además, los modelos están registrados en el
panel de administración de Django."

Mostrar usuarios y el admin.

## 4:25 - 5:00 | Cierre

"El proyecto cumple con los requerimientos: modelos y relaciones uno a muchos, CRUDs completos,
validación de fechas y disponibilidad, formularios con validaciones, Bootstrap, dashboard,
reportes y autenticación. Se probó con 19 pruebas automatizadas que verifican las reglas de
negocio. La documentación técnica y el manual de usuario se incluyen en la carpeta docs.
Gracias por su atención."

Mostrar el diagrama entidad-relación o la carpeta de documentación y terminar.
