# Shipping Service API - Equipo 5

API de Envíos y Logística para el sistema de E-Commerce distribuido.

## Descripción

Este microservicio gestiona la entrega física de pedidos que ya han sido pagados. Se comunica con:
- **Order Service (Equipo 3)**: Para validar pedidos y actualizar su estado
- **Identity Service (Equipo 1)**: Para obtener direcciones de entrega de los clientes

## Tecnologías

- Django 5.2+
- Django REST Framework 3.14+
- drf-spectacular 0.27+ (Documentación Swagger)
- requests 2.31+
- python-dotenv 1.0+
- SQLite (Base de datos)

## Instalación

### 1. Clonar/Navegar al proyecto

```bash
cd ecommerce
```

### 2. Instalar dependencias

```bash
pip3 install -r requirements.txt --break-system-packages
```

O si usas un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura las URLs de los otros microservicios:

```bash
cp .env.example .env
```

Edita `.env` con las IPs correctas de tu red local:

```env
ORDER_SERVICE_URL=http://192.168.1.50:8001
IDENTITY_SERVICE_URL=http://192.168.1.51:8000
```

### 4. Aplicar migraciones

```bash
python3 manage.py migrate
```

### 5. Ejecutar el servidor

```bash
python3 manage.py runserver 0.0.0.0:8002
```

El servidor estará disponible en `http://localhost:8002`

Para acceder desde otros dispositivos en la red local: `http://<tu-ip>:8002`

## Endpoints

### 1. POST /api/shipping/dispatch/

Crea un envío para un pedido pagado.

**Request Body:**
```json
{
  "order_id": 123,
  "payment_id": 456
}
```

**Response 201 Created:**
```json
{
  "id": 1,
  "order_id": 123,
  "tracking_number": "SHIP-20260410-ABC123",
  "carrier": "DHL",
  "delivery_address": "Calle Principal 123, CDMX",
  "status": "Pending",
  "estimated_delivery_date": "2026-04-17"
}
```

**Errores posibles:**
- `400 Bad Request`: Datos inválidos
- `404 Not Found`: Pedido o usuario no encontrado
- `409 Conflict`: El pedido no está en estado "Pagado" o ya tiene un envío
- `503 Service Unavailable`: Servicios externos no disponibles

**Flujo interno:**
1. Valida que el pedido existe en Order Service
2. Verifica que el pedido está en estado "Pagado"
3. Obtiene la dirección de entrega desde Identity Service
4. Genera una guía de rastreo única
5. Asigna paquetería aleatoria (DHL o FedEx)
6. Calcula fecha estimada de entrega
7. Crea registro de envío
8. Actualiza el estado del pedido a "Enviado" en Order Service

### 2. GET /api/shipping/track/{tracking_number}/

Consulta el estado de un envío mediante su guía de rastreo.

**Response 200 OK:**
```json
{
  "tracking_number": "SHIP-20260410-ABC123",
  "status": "In Transit",
  "carrier": "DHL",
  "estimated_delivery_date": "2026-04-17",
  "order_id": 123
}
```

**Errores posibles:**
- `404 Not Found`: Guía de rastreo no encontrada

## Documentación Interactiva (Swagger)

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva en:

- **Swagger UI**: http://localhost:8002/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8002/api/schema/redoc/
- **OpenAPI Schema JSON**: http://localhost:8002/api/schema/

## Modelo de Datos

### Shipment

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID único del envío |
| order_id | Integer | ID del pedido (Order Service) |
| payment_id | Integer | ID del pago (opcional) |
| delivery_address | Text | Dirección completa de entrega |
| tracking_number | String | Guía de rastreo única |
| carrier | String | Paquetería (DHL, FedEx) |
| status | String | Estado (Pending, In Transit, Delivered) |
| estimated_delivery_date | Date | Fecha estimada de entrega |
| created_at | DateTime | Fecha de creación |
| updated_at | DateTime | Última actualización |

## Estados de Envío

- **Pending**: Envío creado, pendiente de recolección
- **In Transit**: En tránsito hacia el destino
- **Delivered**: Entregado al cliente

## Paqueterías

- **DHL**: Entrega estimada en 3-5 días
- **FedEx**: Entrega estimada en 4-7 días

## Estructura del Proyecto

```
ecommerce/
├── ecommerce/                    # Proyecto Django principal
│   ├── settings.py              # Configuración (DRF, Swagger, URLs externas)
│   ├── urls.py                  # URLs principales
│   └── wsgi.py
├── shipping_service/            # App de envíos
│   ├── models.py               # Modelo Shipment
│   ├── serializers.py          # Serializadores DRF
│   ├── views.py                # Vistas (DispatchShipmentView, TrackShipmentView)
│   ├── services.py             # Clientes para APIs externas
│   ├── urls.py                 # URLs de la app
│   └── migrations/             # Migraciones de base de datos
├── .env                         # Variables de entorno (no commitable)
├── .env.example                 # Ejemplo de configuración
├── requirements.txt             # Dependencias Python
├── manage.py                    # Script de gestión Django
└── db.sqlite3                   # Base de datos SQLite
```

## Integración con Otros Microservicios

### Estructura Esperada de Order Service (Equipo 3)

**GET /api/orders/{id}/**
```json
{
  "id": 123,
  "user_id": 45,
  "status": "Pagado",
  "items": [...],
  "total": 1500.00
}
```

**PATCH /api/orders/{id}/status/**
```json
{
  "status": "Enviado"
}
```

### Estructura Esperada de Identity Service (Equipo 1)

**GET /api/users/{id}/profile/**
```json
{
  "id": 45,
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "address": "Calle Principal 123, Colonia Centro, CDMX, 06000"
}
```

**Nota**: El servicio es flexible y acepta diferentes nombres de campos (address, direccion, dirección, direccion_envio, shipping_address).

## Manejo de Errores

El servicio implementa manejo robusto de errores:

1. **Validación de entrada**: Datos inválidos retornan 400
2. **Recursos no encontrados**: 404 con mensaje descriptivo
3. **Conflictos de estado**: 409 con detalles del problema
4. **Servicios externos caídos**: 503 con nombre del servicio afectado
5. **Errores internos**: 500 con logs detallados

## Logging

Los logs se escriben en la consola con el formato:

```
INFO 2026-04-10 12:00:00 shipping_service Requesting order 123 from Order Service
```

Para cambiar el nivel de logging, edita `settings.py`:

```python
LOGGING = {
    ...
    'loggers': {
        'shipping_service': {
            'level': 'DEBUG',  # DEBUG, INFO, WARNING, ERROR
        },
    },
}
```

## Testing Manual

### Usando curl

**Crear envío:**
```bash
curl -X POST http://localhost:8002/api/shipping/dispatch/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": 123, "payment_id": 456}'
```

**Rastrear envío:**
```bash
curl http://localhost:8002/api/shipping/track/SHIP-20260410-ABC123/
```

### Usando Postman

1. Importa la colección desde Swagger UI
2. Configura la URL base: `http://localhost:8002`
3. Ejecuta las peticiones

## Fase de Desarrollo

### Fase 1: Desarrollo con Mocks

Si los otros microservicios no están disponibles, el servicio retornará errores 503 controlados. Puedes simular las respuestas modificando temporalmente los métodos en `services.py`.

### Fase 2: Integración en Red Local

1. Todos deben estar en la misma red WiFi
2. Cada equipo ejecuta su servicio con `0.0.0.0:PUERTO`
3. Configurar `.env` con las IPs locales reales
4. Ejemplo: `ORDER_SERVICE_URL=http://192.168.1.50:8001`

### Obtener tu IP local:

**Linux/Mac:**
```bash
ip addr show | grep inet
# o
ifconfig | grep inet
```

**Windows:**
```cmd
ipconfig
```

## Admin Django

Para gestionar envíos desde el panel de administración:

1. Crear superusuario:
```bash
python3 manage.py createsuperuser
```

2. Registrar el modelo en `shipping_service/admin.py`:
```python
from django.contrib import admin
from .models import Shipment

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order_id', 'carrier', 'status', 'created_at']
    list_filter = ['status', 'carrier']
    search_fields = ['tracking_number', 'order_id']
```

3. Acceder a: http://localhost:8002/admin/

## Contacto

**Equipo 5 - Shipping Service**

Colaboradores:
- Miguel SP
- Daniela (danielita05)

Para dudas sobre la integración con este microservicio, consulta la documentación Swagger o contacta al equipo.

## Licencia

Proyecto académico - UTEZ 2026
