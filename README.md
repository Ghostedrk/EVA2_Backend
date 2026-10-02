# 🚍 Plataforma de Gestión y Reserva de Pasajes — Buses Inter-Sur

Sistema web **full-stack** para la gestión de rutas, buses, servicios y reservas de pasajes. El proyecto está desarrollado con **Django**, **Django REST Framework (DRF)** y un frontend integrado mediante plantillas nativas de Django y **Tailwind CSS**.

La aplicación permite gestionar la disponibilidad de asientos y realizar reservas con control de concurrencia e integridad transaccional para evitar la sobreventa de pasajes.

---

## ✨ Características principales

- **Arquitectura híbrida:** API RESTful protegida mediante autenticación JWT, combinada con vistas renderizadas mediante plantillas nativas de Django.
- **Mapa de asientos dinámico:** la grilla de asientos se genera automáticamente según la capacidad configurada para cada bus.
- **Disponibilidad en tiempo real:** los asientos pendientes y pagados se reflejan como ocupados/deshabilitados en la interfaz.
- **Integridad transaccional:** se utilizan `@transaction.atomic` y `select_for_update` para controlar la concurrencia y evitar la sobreventa de pasajes.
- **Flujo de reserva y compra:** permite seleccionar un asiento, agregarlo al carro y ejecutar un checkout transaccional.

---

## 🛠️ Tecnologías

- **Python 3.10+**
- **Django**
- **Django REST Framework (DRF)**
- **JWT**
- **Tailwind CSS**
- **Base de datos compatible con Django ORM**

---

## 📋 Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- [Python 3.10 o superior](https://www.python.org/)
- [Git](https://git-scm.com/)

Además, el proyecto debe contar con un archivo `requirements.txt` en la raíz del repositorio.

---

## 🚀 Instalación y puesta en marcha

Sigue estos pasos para levantar el proyecto desde cero.

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd <nombre-de-la-carpeta-del-proyecto>
```

### 2. Crear y activar el entorno virtual

En **Windows**:

```bash
python -m venv venv
venv\Scripts\activate
```

En **Linux / macOS**:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear y aplicar las migraciones

Si existen cambios pendientes en los modelos:

```bash
python manage.py makemigrations
```

Luego aplica las migraciones:

```bash
python manage.py migrate
```

### 5. Crear un superusuario

Para acceder al panel de administración de Django:

```bash
python manage.py createsuperuser
```

El comando solicitará los datos necesarios, como nombre de usuario, correo y contraseña.

### 6. Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación quedará disponible en:

```text
http://127.0.0.1:8000/
```

---

## 🧪 Cómo probar la aplicación

Una vez iniciado el servidor, puedes probar el flujo completo de gestión y reserva.

### 1. Crear los datos base

Accede al panel de administración:

```text
http://127.0.0.1:8000/admin/
```

Desde allí:

1. Registra una **Ruta**.
   - Ejemplo: `Temuco → Los Muermos`
2. Registra un **Bus** e indica su capacidad total.
   - Ejemplo: `35` o `40` asientos.
3. Crea un **Servicio** asociando:
   - Ruta
   - Bus
   - Tarifa
   - Fecha de salida

### 2. Probar la interfaz de reservas

Abre:

```text
http://127.0.0.1:8000/reservar/
```

Deberías visualizar las tarjetas de los viajes disponibles, incluyendo:

- Ruta del viaje.
- Tarifa.
- Fecha de salida.
- Grilla de asientos generada de acuerdo con la capacidad real del bus.
- Disponibilidad actual de los asientos.

### 3. Simular una compra

Para probar el flujo de compra:

1. Completa los datos simulados del pasajero:
   - RUT
   - Nombre
2. Selecciona un asiento disponible.
3. El asiento seleccionado cambiará a estado **seleccionado**.
4. Presiona **Agregar al Carro**.
5. Cuando la aplicación lo solicite, introduce tu **Token JWT** de acceso.
6. Presiona **Comprar** para ejecutar el checkout transaccional.

Después de completar la compra, la aplicación debería:

- Recargar la información de disponibilidad.
- Marcar el asiento comprado como **ocupado/bloqueado**.
- Descontar correctamente el asiento del stock disponible.
- Mantener la integridad de la reserva mediante las transacciones del backend.

---

## 🔐 Concurrencia e integridad de las reservas

Uno de los puntos importantes del proyecto es evitar que dos usuarios puedan comprar simultáneamente el mismo asiento.

Para esto, el backend utiliza:

```python
@transaction.atomic
```

junto con:

```python
select_for_update()
```

Esto permite ejecutar las operaciones críticas dentro de una transacción y bloquear las filas correspondientes mientras se procesa la reserva, reduciendo el riesgo de condiciones de carrera y sobreventa.

---

## 📁 Estructura general del proyecto

La estructura exacta puede variar según la organización del repositorio. Como referencia, un proyecto Django de este tipo suele seguir una estructura similar a:

```text
proyecto/
├── manage.py
├── requirements.txt
├── README.md
├── app/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── ...
├── templates/
│   └── ...
└── ...
```

> **Nota:** esta sección es orientativa. El README original no especifica la estructura exacta de carpetas del repositorio.

---

## ⚠️ Notas importantes

- Reemplaza `<url-del-repositorio>` por la URL real del repositorio antes de publicar este README.
- Reemplaza `<nombre-de-la-carpeta-del-proyecto>` por el nombre generado al clonar el repositorio.
- El proyecto requiere que las dependencias indicadas estén disponibles en `requirements.txt`.
- El flujo de compra descrito corresponde al flujo de prueba indicado en la documentación original.

---

## 📌 Resumen del flujo

```text
Administrador
    │
    ├── Crear Ruta
    ├── Crear Bus
    └── Crear Servicio
             │
             ▼
       Viajes disponibles
             │
             ▼
      Seleccionar asiento
             │
             ▼
        Agregar al carro
             │
             ▼
      Autenticación JWT
             │
             ▼
       Checkout transaccional
             │
             ▼
       Asiento ocupado
```

---

## 👨‍💻 Desarrollo

Para trabajar localmente sobre el proyecto, activa siempre el entorno virtual antes de ejecutar comandos de Django:

```bash
venv\Scripts\activate
```

Y utiliza:

```bash
python manage.py runserver
```

para iniciar el servidor de desarrollo.

---