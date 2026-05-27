# 🎓 PREGUNTAS QUE TE VAN A HACER (Y LAS RESPUESTAS)

**Prepárate con estas respuestas para el jueves**

---

## CATEGORÍA 1: ARQUITECTURA LIMPIA

### P1: ¿Qué es Arquitectura Limpia y por qué la usaste?

**R:** Arquitectura Limpia es un patrón que separa la aplicación en capas independientes:

- **Domain:** Lógica de negocio pura (entidades, casos de uso)
- **Application:** Orquestación de la lógica (servicios)
- **Infrastructure:** Detalles técnicos (BD, frameworks)
- **Presentation:** Capa de API (FastAPI, controllers)

**Ventajas:**
✅ Independencia de frameworks (cambiar BD, API, etc. sin afectar lógica)
✅ Testeable (lógica sin dependencias externas)
✅ Mantenible (cambios localizados)
✅ Escalable (agregar nuevos casos de uso)

**En mi proyecto:**
- `app/domain/` → Entidades (User, Payment)
- `app/application/` → Servicios (AuthService, PaymentService)
- `app/infrastructure/` → BD, caché, workers
- `app/presentation/` → Rutas FastAPI

---

### P2: ¿Cómo aplicaste Domain-Driven Design (DDD)?

**R:** DDD enfatiza que el código debe reflejar el dominio del negocio:

- **Entidades:** User, Payment (tienen identidad única)
- **Value Objects:** Email, Currency (sin identidad, solo valores)
- **Agregados:** Payment es agregado de Transaction
- **Servicios:** AuthService (lógica que no pertenece a una entidad)
- **Repositorios:** Abstracción de la persistencia

**En mi proyecto:**
```python
# Domain Entity (app/domain/models/payment.py)
class Payment:
    id: UUID
    merchant_id: str
    amount: Decimal
    currency: Currency  # Value Object
    status: PaymentStatus
    
# Application Service (app/application/services/payment_service.py)
class PaymentService:
    def create_payment(self, merchant_id, amount, currency):
        # Lógica de negocio aquí
```

---

### P3: ¿Explicame el flujo de un pago desde que llega hasta que se completa?

**R:** Explicando paso a paso:

```
1. POST /api/v1/payments/ (Usuario + Token JWT)
   ↓
2. PaymentController.create_payment() recibe request
   ↓
3. PaymentService.create_payment() valida:
   - ✅ Usuario autenticado (JWT válido)
   - ✅ Monto > 0
   - ✅ Moneda válida (USD, EUR, GBP)
   - ✅ Método válido (card, bank_transfer, wallet)
   ↓
4. Crear objeto Payment(status="pending")
   ↓
5. Guardar en BD (SQLAlchemy ORM)
   ↓
6. Encolar en Queue (thread-safe)
   ↓
7. 3 Workers en Thread consumen la Queue:
   - Worker 1: Obtiene Payment
   - Worker 2: Calcula comisión (%)
   - Worker 3: Convierte a USD (con ReadWriteLock)
   ↓
8. Actualizar Payment(status="completed", commission=X, amount_usd=Y)
   ↓
9. Guardar en BD
   ↓
10. Actualizar MetricsCollector (thread-safe con RLock)
    ↓
11. Cliente hace GET /payments/<id> → Retorna "completed"
```

---

## CATEGORÍA 2: SEGURIDAD

### P4: ¿Cómo protegiste las contraseñas?

**R:** Con bcrypt (hashing criptográfico):

```python
from bcrypt import hashpw, gensalt, checkpw

# Al registrar:
password_hash = hashpw(password.encode(), gensalt(rounds=12))
# Genera salt aleatorio + hash seguro

# Al login:
if checkpw(password.encode(), user.password_hash):
    # Contraseña correcta
```

**Ventajas:**
- ✅ Irreversible (no se puede obtener password del hash)
- ✅ Resistant a força bruta (rounds=12 = ~100ms por intento)
- ✅ Cada password tiene salt único
- ✅ Estándar de la industria

---

### P5: ¿Cómo funciona JWT y por qué es mejor que sesiones?

**R:** JWT = JSON Web Token

**Estructura:**
```
header.payload.signature
```

**Ejemplo:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VyX2lkIjoiMTIzIiwiZW1haWwiOiJqdWFuQGV4YW1wbGUuY29tIiwiaWF0IjoxNjI2MDAwMDAwLCJleHAiOjE2MjYwMDM2MDB9.
xvzLJ7T3L_kJ5l3T_k5L_k7L_k9L_k1L_k3L_k5L_k7
```

**Ventajas sobre sesiones:**
- ✅ Stateless (no necesita guardar sesión en servidor)
- ✅ Escalable (múltiples servidores sin sincronización)
- ✅ Distribuido (funciona con microservicios)
- ✅ Mobile-friendly (mejor para apps móviles)

**Flujo:**
```
1. Cliente: POST /login → Envía email + password
2. Servidor: Verifica, genera JWT con secret key
3. Cliente: Guarda token en memoria/localStorage
4. Cliente: Cada request incluye "Authorization: Bearer <token>"
5. Servidor: Decodifica token con secret key
6. Servidor: Valida firma + expiración
7. Servidor: Extrae información (user_id, email)
```

---

### P6: ¿Cómo protegiste los endpoints administrativos?

**R:** Con Role-Based Access Control (RBAC):

```python
# En app/presentation/deps.py
def get_current_user(...):
    # 1. Obtiene usuario del JWT
    user = JWT_SERVICE.decode(token)
    # 2. Retorna usuario autenticado

@router.get("/admin/metrics")
async def get_metrics(current_user = Depends(get_current_user)):
    # 3. Verifica que sea admin
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(403, "Solo administradores")
    # 4. Retorna métricas
```

**Flujo:**
- ✅ Usuario sin token → 401 Unauthorized
- ✅ Usuario con token inválido → 401
- ✅ Usuario normal con token válido → 403 Forbidden
- ✅ Admin con token válido → 200 OK

---

## CATEGORÍA 3: CONCURRENCIA

### P7: ¿Cómo implementaste los Workers para procesar pagos?

**R:** Patrón Productor-Consumidor con threading.Thread:

```python
# PRODUCTOR (API)
payment = Payment(status="pending")
queue.put(payment)  # Encolar

# CONSUMIDOR (3 Workers)
class PaymentWorker(Thread):
    def run(self):
        while True:
            payment = queue.get()  # Espera si vacía
            # Procesa pago
            payment.status = "completed"
            # Actualiza BD
            queue.task_done()

# Inicio
for i in range(3):
    worker = PaymentWorker(daemon=True)
    worker.start()
```

**Ventajas:**
- ✅ Asincrónico (no bloquea API)
- ✅ Escalable (agregar más workers)
- ✅ Tolerancia a fallos (reintenta si falla)
- ✅ Thread-safe (Queue.queue es inmune a race conditions)

---

### P8: ¿Qué es RLock y por qué lo usaste en MetricsCollector?

**R:** RLock = Recursive Lock (Re-entrant Lock)

```python
from threading import RLock

class MetricsCollector:
    def __init__(self):
        self._lock = RLock()
        self._metrics = {...}
    
    def record_payment(self, payment):
        with self._lock:  # Adquiere lock
            self._metrics["total"] += 1
            self._metrics["amount_usd"] += payment.amount_usd
        # Libera lock
```

**Diferencia Lock vs RLock:**
- **Lock:** Si un thread intenta adquirir 2 veces → Deadlock
- **RLock:** Un thread PUEDE adquirir múltiples veces (si la libera igual)

**En mi proyecto:**
- 3 Workers escriben en MetricsCollector simultáneamente
- Sin RLock → Race condition (valores corruptos)
- Con RLock → Todo thread-safe

---

### P9: ¿Explicame el ReadWriteLock que implementaste?

**R:** ReadWriteLock permite:
- ✅ Múltiples **lectores** simultáneos (lectura compartida)
- ✅ Un único **escritor** (escritura exclusiva)
- ✅ Los escritores tienen prioridad

**Caso de uso:**
```python
# En PaymentConfig:
# - Cientos de threads leen tasas de cambio (get_rate)
# - Ocasionalmente, se actualiza una tasa (update_rates)
```

**Implementación:**
```python
class ReadWriteLock:
    def acquire_read(self):
        # Múltiples threads pueden entrar aquí
        self._read_count += 1
    
    def release_read(self):
        self._read_count -= 1
    
    def acquire_write(self):
        # Solo UN thread aquí (bloquea lectores)
        while self._read_count > 0:
            wait()
    
    def release_write(self):
        # Despierta lectores/escritores en espera
        notify_all()
```

**Ventaja:**
- Sin ReadWriteLock: 1 thread accede tasas → Lento
- Con ReadWriteLock: Cientos de threads leen en paralelo → Rápido

---

### P10: ¿Qué es threading.Barrier y para qué lo usaste?

**R:** Barrier = Punto de sincronización donde N threads se esperen

```python
# Crear barrier para 3 threads
barrier = threading.Barrier(3)

def worker(currency):
    # Convierte moneda a USD
    result = convert(currency)
    
    # Espera a los otros 2 threads
    barrier.wait()  # Todos esperan aquí
    
    # Cuando los 3 llegan, todos continúan
    print(f"¡Los 3 threads se sincronizaron!")

# Inicio
threads = []
for curr in ["USD", "EUR", "GBP"]:
    t = Thread(target=worker, args=(curr,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

**En mi proyecto (Exercise 9):**
```python
# PaymentSettlement
class PaymentSettlement:
    def __init__(self):
        self.barrier = threading.Barrier(3)  # 3 monedas
    
    def convert_to_usd(self, currency, amount, thread_id):
        converted = amount * RATES[currency]
        self.barrier.wait()  # Todos esperan aquí
        return converted
```

**Ventaja:**
- Todos los threads convierten simultáneamente
- Se sincronizan antes de consolidar el total
- Simula operaciones paralelas realistas

---

## CATEGORÍA 4: BASE DE DATOS

### P11: ¿Qué ORM usaste y por qué?

**R:** SQLAlchemy (ORM de Python)

**Ventajas:**
- ✅ Agnóstico de BD (PostgreSQL, MySQL, SQLite, etc.)
- ✅ Queries type-safe
- ✅ Migrations (Alembic)
- ✅ Relaciones (OneToMany, ManyToMany)

```python
# Modelo
class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)

# Query
user = db.query(User).filter(User.email == "juan@example.com").first()
```

---

### P12: ¿Cómo manejaste las migraciones de BD?

**R:** Con Alembic (herramienta de migraciones para SQLAlchemy)

```bash
# Crear migración
alembic revision --autogenerate -m "Add payments table"

# Ejecutar
alembic upgrade head
```

**En Docker:**
```dockerfile
# En Dockerfile
RUN alembic upgrade head
```

---

## CATEGORÍA 5: TESTING

### P13: ¿Cómo testeaste el JWT?

**R:** Con pytest:

```python
# tests/test_auth.py
def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "email": "juan@example.com",
        "password": "Password123",
        "full_name": "Juan"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "juan@example.com"

def test_invalid_email():
    response = client.post("/api/v1/auth/register", json={
        "email": "invalid",
        "password": "Password123"
    })
    assert response.status_code == 422

def test_login_success():
    # Primero registrar
    client.post("/api/v1/auth/register", json={...})
    
    # Luego login
    response = client.post("/api/v1/auth/login", json={
        "email": "juan@example.com",
        "password": "Password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

### P14: ¿Cómo testeaste los pagos concurrentes?

**R:** Con pytest-asyncio y mocking:

```python
# tests/test_payments.py
@pytest.mark.asyncio
async def test_payment_created_with_pending_status():
    response = await client.post("/api/v1/payments/", 
        json={
            "merchant_id": "MERCHANT_001",
            "amount": 100.0,
            "currency": "USD",
            "method": "card"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"

@pytest.mark.asyncio
async def test_payment_processed_by_workers():
    # Crear pago
    response = await client.post("/api/v1/payments/", json={...})
    payment_id = response.json()["id"]
    
    # Esperar workers
    await asyncio.sleep(3)
    
    # Verificar completado
    response = await client.get(f"/api/v1/payments/{payment_id}")
    assert response.json()["status"] == "completed"
    assert response.json()["commission"] > 0
```

---

## CATEGORÍA 6: PATRONES DE DISEÑO

### P15: ¿Qué patrones de diseño usaste?

**R:**

| Patrón | Ubicación | Caso de uso |
|--------|-----------|-----------|
| **Singleton** | `MetricsCollector` | Una única instancia compartida |
| **Repository** | `PaymentRepositorySQL` | Abstracción de BD |
| **Factory** | `PaymentServiceFactory` | Crear servicios |
| **Dependency Injection** | `FastAPI Depends()` | Inyectar dependencias |
| **Strategy** | `PaymentMethod` (card/bank/wallet) | Diferentes estrategias de pago |
| **Observer** | Eventos de pago | Notificación de cambios |
| **Worker Pool** | 3 Threads procesando | Procesamiento concurrente |
| **Producer-Consumer** | Queue + Workers | Productor (API) → Consumidor (Workers) |
| **Read-Write Lock** | `PaymentConfig` | Lectores concurrentes + escritor exclusivo |
| **Barrier Sync** | `PaymentSettlement` | Sincronización de N threads |

---

## CATEGORÍA 7: ERRORES Y CÓMO LOS SOLUCIONASTE

### P16: ¿Qué errores encontraste y cómo los solucionaste?

**R:** Los principales fueron:

**1. "database 'user' does not exist"**
- **Causa:** PostgreSQL healthcheck intentaba conectarse a BD "user" (default)
- **Solución:** Especificar `-d taller_final` en healthcheck

**2. "ModuleNotFoundError: email_validator"**
- **Causa:** Pydantic EmailStr necesitaba email-validator externo
- **Solución:** Agregar `email-validator==2.1.0` a requirements.txt

**3. "401 Unauthorized" en todos los endpoints**
- **Causa:** FastAPI no recibía Authorization header correctamente
- **Solución:** Usar `Header(None)` en lugar de parámetro normal

**4. Race condition en MetricsCollector**
- **Causa:** 3 workers escribían simultáneamente sin sincronización
- **Solución:** Usar `threading.RLock()` para proteger acceso compartido

---

## PREGUNTAS CAPCIOSAS (Prepárate)

### P17: ¿Qué pasa si un pago falla?

**R:** El worker lo reintentar (con límite de reintentos):
```python
class PaymentWorker:
    def run(self):
        payment = queue.get()
        retries = 0
        max_retries = 3
        
        while retries < max_retries:
            try:
                process_payment(payment)
                break
            except Exception:
                retries += 1
                time.sleep(2 ** retries)  # Backoff exponencial
        
        if retries == max_retries:
            payment.status = "failed"
```

---

### P18: ¿Qué pasa si el servidor se cae mientras procesa pagos?

**R:** Los pagos en "pending" se pierden (sin persistencia de cola).
**Solución real:** Guardar pagos en BD primero, luego procesar.

---

### P19: ¿Escalas bien? ¿Qué limitaciones tiene?

**R:** 
- ✅ Bien para proyecto académico
- ❌ Limitaciones reales:
  - Solo 3 workers (no horizontal)
  - Sin persistencia de cola
  - Sin retry store
  - Sin monitoring
  
**Para producción:**
- Usar Celery + Redis (cola distribuida)
- Usar APScheduler (scheduler)
- Usar Prometheus (monitoreo)

---

## RESPUESTAS CORTAS Y PODEROSAS

Memoriza estas frases clave:

1. **"Arquitectura Limpia permite cambiar tecnologías sin afectar lógica de negocio"**

2. **"JWT es stateless y escalable, ideal para microservicios"**

3. **"RLock previene race conditions en acceso compartido"**

4. **"Los Workers desacoplan el procesamiento de la API"**

5. **"ReadWriteLock permite múltiples lectores pero escritor exclusivo"**

6. **"Barrier sincroniza N threads en un punto"**

7. **"Bcrypt con rounds=12 es resistente a fuerza bruta"**

8. **"RBAC controla acceso basado en roles"**

9. **"SQLAlchemy es agnóstico de BD"**

10. **"pytest valida el comportamiento de cada componente"**

---

**¡Buena suerte el jueves! 🚀**

