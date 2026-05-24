# Taller Final - Sistema Distribuido con Arquitectura Limpia

## 📋 Descripción General

Sistema distribuido concurrente que implementa los ejercicios 1, 7 y 9 del taller, con énfasis en:

- **Ejercicio 1**: Gestión de usuarios y autenticación segura con JWT
- **Ejercicio 7**: Dashboard administrativo con métricas de concurrencia
- **Ejercicio 9**: Sistema de pagos internacionales con procesamiento concurrente

Construido con **Arquitectura Limpia** (Clean Architecture) y **Docker** para máxima escalabilidad y mantenibilidad.

## 🏗️ Arquitectura

### Capas de la Arquitectura Limpia

```
┌─────────────────────────────────────────────┐
│     PRESENTATION (FastAPI, Schemas)         │
│  - Routers: auth, payment, metrics          │
│  - DTOs (Pydantic)                         │
│  - Dependencias (Dependency Injection)      │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│     APPLICATION (Servicios)                  │
│  - AuthService                              │
│  - PaymentService                           │
│  - JWTService                               │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│     DOMAIN (Lógica de Negocio)              │
│  - Entidades: User, Payment                 │
│  - Value Objects: Email, Password           │
│  - Puertos: Interfaces                      │
│  - Excepciones de Dominio                   │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│     INFRASTRUCTURE (Implementaciones)        │
│  - Repositorios (SQLAlchemy)                │
│  - Security (Bcrypt)                        │
│  - Concurrency (Workers, Metrics)           │
│  - Database (PostgreSQL)                    │
└─────────────────────────────────────────────┘
```

### Estructura de Carpetas

```
.
├── app/
│   ├── domain/               # Lógica de negocio pura
│   │   ├── entities/         # User, Payment
│   │   ├── value_objects/    # Email, Password
│   │   ├── ports/            # Interfaces (Repositories, etc)
│   │   ├── constants.py      # Enums y constantes
│   │   └── exceptions.py     # Excepciones de dominio
│   ├── application/          # Servicios de aplicación
│   │   └── services/         # AuthService, PaymentService, JWTService
│   ├── infrastructure/       # Implementaciones externas
│   │   ├── database/         # SQLAlchemy models, session
│   │   ├── repositories/     # Implementaciones de puertos
│   │   ├── security/         # Bcrypt hasher
│   │   ├── concurrency/      # Metrics, Workers
│   │   └── workers/          # PaymentWorker, WorkerPool
│   ├── presentation/         # FastAPI, Controllers
│   │   ├── api/              
│   │   │   └── routers/      # auth.py, payment.py, metrics.py
│   │   ├── schemas/          # DTOs (Pydantic)
│   │   └── deps.py           # Dependency injection
│   ├── config.py             # Settings
│   └── main.py               # FastAPI app
├── tests/                    # Tests unitarios
├── docker-compose.yml        # Orquestación de servicios
├── Dockerfile                # Imagen de la app
├── requirements.txt          # Dependencias Python
└── .env                      # Variables de entorno
```

## 🔐 Ejercicio 1: Autenticación con JWT

### Características

- ✅ Registro seguro con validación de email y contraseña
- ✅ Hash de contraseña con **bcrypt** (12 rounds)
- ✅ Generación de JWT con expiración de 24 horas
- ✅ Autenticación stateless
- ✅ Protección de endpoints con middleware de autorización

### Endpoints

```bash
# Registro
POST /api/v1/auth/register
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "MyPassword123",
  "full_name": "Usuario Test"
}

# Login
POST /api/v1/auth/login
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "MyPassword123"
}

# Respuesta
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "uuid",
  "email": "user@example.com"
}
```

### Validaciones (Domain)

```python
class Email(ValueObject):
    # Email válido: regex pattern
    
class Password(ValueObject):
    # Min 8 caracteres
    # Mínimo 1 mayúscula
    # Mínimo 1 número
```

## 📊 Ejercicio 7: Dashboard Administrativo con Métricas

### Características

- ✅ Recolección de métricas thread-safe con `RLock`
- ✅ Cálculo de tasas de éxito y promedios
- ✅ Monitoreo de estado del sistema (threads activos)
- ✅ API protegida solo para administradores
- ✅ Reinicio de métricas bajo demanda

### Endpoint

```bash
# Obtener métricas (solo admin)
GET /api/v1/admin/metrics
Authorization: Bearer {token}

# Respuesta
{
  "timestamp": "2024-01-15T10:30:00",
  "uptime_seconds": 125.5,
  "payments": {
    "processed": 15,
    "failed": 2,
    "total": 17,
    "success_rate_percent": 88.24,
    "total_amount_usd": 3500.50,
    "last_payment_time": "2024-01-15T10:29:55",
    "avg_payment_interval_seconds": 7.45
  },
  "users": {
    "registered": 5,
    "logins": 12
  },
  "system": {
    "thread_count": 8
  }
}
```

### Seguridad

- Solo usuarios con email en lista `admin@taller.local` pueden acceder
- Todas las operaciones se registran en métricas
- Thread-safe con sincronización

## 💳 Ejercicio 9: Pagos Internacionales

### Características

- ✅ Cola thread-safe (`queue.Queue`) con capacidad máxima
- ✅ Pool de 3 workers procesando concurrentemente
- ✅ Simulación de validación antifraude
- ✅ Cálculo de comisión por método de pago
- ✅ Conversión de monedas (EUR, GBP, JPY → USD)
- ✅ Estados de pago: PENDING → PROCESSING → COMPLETED

### Patrón Productor-Consumidor

```
Productores (threads)     Cola Thread-Safe     Consumidores (Workers)
    │                           │                      │
    ├─ Productor 1 ─────→ [Pago 1]                Worker 1
    │                      [Pago 2] ────────→    Worker 2
    ├─ Productor 2 ─────→ [Pago 3]                Worker 3
    │                      [Pago 4]
    └─ Productor N ─────→ [Pago N]
    
Capacidad máxima: 20 pagos
```

### API

```bash
# Crear pago
POST /api/v1/payments/
Authorization: Bearer {token}
Content-Type: application/json
{
  "merchant_id": "MERCHANT_001",
  "amount": 150.50,
  "currency": "EUR",
  "method": "card"
}

# Respuesta
{
  "id": "payment-uuid",
  "merchant_id": "MERCHANT_001",
  "amount": 150.50,
  "currency": "EUR",
  "method": "card",
  "status": "pending",
  "commission": 7.53,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}

# Consultar estado
GET /api/v1/payments/{payment_id}
Authorization: Bearer {token}

# Respuesta
{
  "payment_id": "payment-uuid",
  "status": "completed",
  "amount": 150.50,
  "currency": "EUR",
  "commission": 7.53,
  "net_amount": 142.97
}
```

### Comisiones por Método

| Método | Comisión |
|--------|----------|
| Tarjeta | 5% |
| Transferencia Bancaria | 2% |
| Wallet | 1% |

### Tasas de Cambio (Simuladas)

| Moneda | Tasa |
|--------|------|
| USD | 1.0 |
| EUR | 1.08 |
| GBP | 1.25 |
| JPY | 0.0067 |

## 🚀 Instalación y Uso

### Requisitos

- Docker y Docker Compose
- Python 3.11+ (si ejecutar sin Docker)
- PostgreSQL 15+

### Con Docker (Recomendado)

```bash
# Clonar/descargar proyecto
cd "c:\Users\JUAN ZULUAGA\Desktop\ACS\Taller Final"

# Iniciar servicios
docker-compose up -d

# Verificar que está corriendo
docker-compose ps

# Ver logs
docker-compose logs -f app

# Detener
docker-compose down
```

### Sin Docker

```bash
# Crear entorno virtual
python -m venv venv
source venv/Scripts/activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar BD (PostgreSQL debe estar corriendo)
# Actualizar DATABASE_URL en .env

# Ejecutar migraciones (si existen)
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Acceso

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432

## 🧪 Tests

### Ejecutar todos los tests

```bash
pytest

# Con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_auth_service.py -v
pytest tests/test_metrics.py -v
pytest tests/test_payment_service.py -v
```

### Tests Implementados

- ✅ Value Objects (Email, Password)
- ✅ Bcrypt Hasher
- ✅ AuthService (register, authenticate)
- ✅ PaymentService (validación, comisiones, conversión)
- ✅ MetricsCollector (thread-safety)

## 🎮 Demo del Ejercicio 9

Ejecutar demostración completa del sistema de pagos:

```bash
python demo_payment_exercise9.py
```

Muestra:
- Productores generando pagos
- Workers procesando concurrentemente
- Métricas en tiempo real
- Conversión de monedas

## 📈 Características de Concurrencia

### Thread-Safety

- `RLock` para proteger métricas
- `queue.Queue` thread-safe nativa
- `threading.Event` para señales de parada

### Workers (Ejercicio 9)

```python
class PaymentWorker(threading.Thread):
    # 3 workers procesando concurrentemente
    # Simulan: validación antifraude, cálculo de comisión
    # Actualizan BD de forma atómica
    # Registran métricas
```

### Patrón Productor-Consumidor

- Desacoplamiento entre productores y consumidores
- Backpressure automático (cola llena → espera)
- Procesamiento asincrónico

## 🔒 Seguridad

### Implementado

- ✅ Contraseñas hasheadas con bcrypt
- ✅ JWT con expiración
- ✅ Validación de email (regex)
- ✅ Validación de contraseña (min 8 chars, mayúscula, número)
- ✅ Acceso basado en roles (admin)
- ✅ CORS configurado
- ✅ Middleware de autenticación

### No en Producción

⚠️ **Cambiar antes de producción:**
- `SECRET_KEY` en `.env`
- Usar HTTPS
- Configurar CORS apropiadamente
- Usar BD en producción (no SQLite)
- Configurar secrets manager

## 📝 Patrón de Diseño

### Arquitectura Limpia

1. **Independencia de Frameworks**: Lógica de negocio en Domain
2. **Independencia de UI**: Controllers solo traducen HTTP → servicios
3. **Independencia de BD**: Repositorios abstraen almacenamiento
4. **Testeable**: Todos los componentes pueden testearse unitariamente
5. **Independencia de detalles externos**: Puertos definen contratos

### Patrones Aplicados

- **Repository**: Abstrae acceso a datos
- **Factory**: Creación de entidades (User, Payment)
- **Strategy**: Diferentes hashers, diferentes métodos de pago
- **Dependency Injection**: FastAPI dependencies
- **Value Object**: Email, Password con validaciones
- **Producer-Consumer**: Sistema de pagos
- **Worker Pool**: Procesamiento concurrente
- **Singleton**: MetricsCollector global
- **Observer**: Métricas escuchando eventos

## 🧠 Conceptos Clave

### Dominio vs Infraestructura

```python
# DOMINIO - Lógica pura, sin dependencias
class User:
    def __init__(self, email, hashed_password):
        self.email = Email(email)  # Valida
        
# INFRAESTRUCTURA - Implementación de BD
class UserRepositorySQLAlchemy:
    def save(self, user: User):
        db_user = UserModel(...)  # Mapea a BD
```

### Value Objects

```python
# Valida al crear, nunca estado inválido
password = Password("MyPass123")  # OK
password = Password("weak")        # Excepción

# Email normalizado
email1 = Email("USER@EXAMPLE.COM")
email2 = Email("user@example.com")
# email1 == email2  (ambos son "user@example.com")
```

### Inversión de Control

```python
# Servicio no conoce dónde se guarda el usuario
class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository  # Inyectado
    
    async def register(self, email, password):
        user = User(...)
        await self.repo.save(user)  # Polimórfico
```

## 📚 Referencias

- Clean Architecture - Robert C. Martin
- Domain-Driven Design - Eric Evans
- FastAPI Documentation
- SQLAlchemy ORM
- Python Threading

## 👨‍💻 Autor

Taller Final - Sistema Distribuido
Implementado con Arquitectura Limpia y Docker

## 📄 Licencia

MIT License

---

**Última actualización**: Enero 2024
