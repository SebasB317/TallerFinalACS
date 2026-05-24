# 📖 EXPLICACIÓN DETALLADA - Cómo Funciona Todo

## 📌 Índice

1. [Ejercicio 1: Autenticación JWT](#ejercicio-1-autenticación-jwt)
2. [Ejercicio 7: Métricas](#ejercicio-7-métricas)
3. [Ejercicio 9: Pagos Internacionales](#ejercicio-9-pagos-internacionales)
4. [Por qué Arquitectura Limpia](#por-qué-arquitectura-limpia)
5. [Cómo Modularizamos](#cómo-modularizamos)
6. [Ejecutar Todo](#cómo-ejecutar-todo)

---

# EJERCICIO 1: AUTENTICACIÓN JWT

## ¿QUÉ ES?

Un sistema que permite:
- **Registrar** usuarios con email y contraseña segura
- **Autenticar** usuarios (login)
- **Generar tokens** JWT para acceso protegido
- **Validar tokens** en cada petición

## FLUJO DE FUNCIONAMIENTO

### Registrar Usuario

```
USUARIO                    API (Presentation)        AuthService (Application)      Repository (Infrastructure)     Database
   │                            │                            │                            │                         │
   ├─ POST /register ──────────→│                            │                            │                         │
   │   {                        │                            │                            │                         │
   │    email: "user@test.com"  ├─ Crear UserRequest ──────→│                            │                         │
   │    password: "Pass123"     │                            ├─ Validar Email VO         │                         │
   │   }                        │                            ├─ Validar Password VO      │                         │
   │                            │                            ├─ Hash con bcrypt ────────→│ (12 rounds)             │
   │                            │                            │                            │                         │
   │                            │                            ├─ Crear User Entity ──────→│                         │
   │                            │                            │                            ├─ INSERT user ─────────→│
   │                            │                            │                            │                         │ ✅ Guardado
   │                            │                            │                            │←────────────────────────┤
   │←─────────────────────────────── UserResponse ────────────────────────────────────────│                         │
   │   {                                                                                    │                         │
   │    id: "uuid-123",                                                                    │                         │
   │    email: "user@test.com"                                                             │                         │
   │   }                                                                                    │                         │
```

### Login de Usuario

```
USUARIO                    API (Presentation)        AuthService (Application)      Repository (Infrastructure)     JWTService          Database
   │                            │                            │                            │                            │                  │
   ├─ POST /login ────────────→│                            │                            │                            │                  │
   │   {                        │                            │                            │                            │                  │
   │    email: "user@test.com"  ├─ Crear LoginRequest ─────→│                            │                            │                  │
   │    password: "Pass123"     │                            ├─ Email VO ────────────────→│ find_by_email ──────────→│ SELECT user       │
   │   }                        │                            │                            │                            │←──────────────────┤
   │                            │                            │                    user{...}                            │
   │                            │                            ├─ bcrypt.verify(pass, hash) (en memoria)               │
   │                            │                            │ ✅ Válido                                              │
   │                            │                            ├─ create_token ────────────────────────────────────────→│
   │                            │                            │                            │                    JWT: "eyJhbGc..."
   │←─────────────────────────────── TokenResponse ──────────────────────────────────────────────────────────────────│
   │   {                                                                                                                │
   │    access_token: "eyJhbGc...",                                                                                    │
   │    token_type: "bearer",                                                                                          │
   │    user_id: "uuid-123"                                                                                            │
   │   }                                                                                                                │
```

### Acceder a Endpoint Protegido

```
USUARIO                    API (Presentation)              FastAPI Depends              JWTService              Repository
   │                            │                              │                           │                         │
   ├─ GET /admin/metrics ──────→│                              │                           │                         │
   │   Authorization:           │                              │                           │                         │
   │   Bearer eyJhbGc... ────────├─ get_current_user ────────→│                           │                         │
   │                            │  (middleware)               ├─ verify_token ───────────→│                         │
   │                            │                              │                    JWT válido
   │                            │                              │←──────────────────────────┤
   │                            │                              │ payload = {sub: "uuid-123", email: "user@test.com"}
   │                            │                              ├─ get_user ────────────────────────────────────────→│
   │                            │                              │                           │         find_by_id ─→│
   │                            │                              │                           │                    user{...}
   │←───────────────────────────────── Metrics ───────────────────────────────────────────│                    │
```

## CÓDIGO IMPORTANTE

### 1. Value Objects (Domain)

**Por qué**: Validar en construcción, nunca estado inválido.

```python
# app/domain/value_objects/email.py
class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):  # ← FALLO TEMPRANO
            raise InvalidEmailException(f"Email inválido: {value}")
        self.value = value.lower()  # ← NORMALIZADO
```

**Beneficio**: Si `Email("invalid")` se crea, siempre es válido.

### 2. Entity (Domain)

**Por qué**: Encapsular lógica de negocio de Usuario.

```python
# app/domain/entities/user.py
class User:
    def __init__(self, id, email, hashed_password, ...):
        self.id = id
        self.email = email  # Email VO
        self.hashed_password = hashed_password
    
    def deactivate(self):  # ← LÓGICA DE NEGOCIO
        self.is_active = False
```

**Beneficio**: Lógica de negocio separada de BD.

### 3. Puerto (Interface)

**Por qué**: Abstraer dónde se guarda el usuario.

```python
# app/domain/ports/user_repository.py
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass
```

**Beneficio**: Cambiar de SQLAlchemy a MongoDB sin tocar Domain.

### 4. Servicio (Application)

**Por qué**: Orquestar el flujo de negocio.

```python
# app/application/services/auth_service.py
class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,  # ← INYECTADO
        password_hasher: PasswordHasher,
        metrics_collector: MetricsCollector
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.metrics = metrics_collector
    
    async def register(self, email: str, password: str) -> User:
        # 1. Validar Value Objects
        email_vo = Email(email)  # ← Falla aquí si inválido
        password_vo = Password(password)
        
        # 2. Verificar no existe
        existing = await self.user_repository.find_by_email(email)
        if existing:
            raise UserAlreadyExistsException(...)
        
        # 3. Hash seguro
        hashed_password = self.password_hasher.hash(password_vo.value)
        
        # 4. Crear entidad
        user = User(
            id=str(uuid.uuid4()),
            email=email_vo.value,
            hashed_password=hashed_password
        )
        
        # 5. Persistir
        await self.user_repository.save(user)
        
        # 6. Registrar métrica
        self.metrics.record_user_registered()
        
        return user
```

**¿Por qué cada paso?**
- Paso 1: Value Objects validan = estado consistente
- Paso 2: Regla de negocio = email único
- Paso 3: Seguridad = no guardamos plaintext
- Paso 4: Entidad = agregado coherente
- Paso 5: Persistencia = separada de lógica
- Paso 6: Observabilidad = registrar eventos

### 5. JWT Service (Application)

**Por qué**: Generar y verificar tokens.

```python
# app/application/services/jwt_service.py
class JWTService:
    def create_token(self, user_id: str, email: str) -> str:
        payload = {
            "sub": user_id,              # ← Identificador
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=24),  # ← EXPIRACIÓN
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    def verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:  # ← Token pasado
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:      # ← Token manipulado
            raise ValueError("Token inválido")
```

**¿Por qué así?**
- `exp`: Token no vive forever (seguridad)
- `iat`: Cuándo se creó (auditoría)
- Try/except: Fallos claros (no cryptic errors)

### 6. Router (Presentation)

**Por qué**: HTTP ↔ Servicios.

```python
# app/presentation/api/routers/auth.py
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: RegisterRequest,  # ← DTO (Pydantic)
    auth_service: AuthService = Depends(get_auth_service)  # ← Inyección
):
    try:
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active
        )
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
```

**¿Por qué así?**
- `RegisterRequest`: Valida JSON (Pydantic)
- `Depends()`: FastAPI maneja inyección
- Try/except: Convierte excepciones a HTTP
- `UserResponse`: DTO ≠ Entidad (separación)

### 7. Infraestructura (Repository)

**Por qué**: Implementación concreta de persistencia.

```python
# app/infrastructure/repositories/user_repository_sqlalchemy.py
class UserRepositorySQLAlchemy(UserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, user: User) -> None:
        # Mapear Entidad → Modelo BD
        db_user = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            ...
        )
        self.db.add(db_user)
        self.db.commit()
    
    async def find_by_email(self, email: str) -> Optional[User]:
        result = self.db.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        db_user = result.scalars().first()
        return db_user.to_entity() if db_user else None  # ← Modelo → Entidad
```

**¿Por qué así?**
- Mapeo: BD ↔ Domain separados
- `to_entity()`: Reconstruir objeto dominio
- Query: SQL optimizado (Índices, etc)

### 8. Seguridad (Bcrypt)

**Por qué**: Hash irreversible de contraseñas.

```python
# app/infrastructure/security/bcrypt_hasher.py
class BcryptHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)  # ← 12 ROUNDS
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def verify(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
```

**¿Por qué Bcrypt 12 rounds?**
- Cada round ≈ duplica tiempo (defensa contra fuerza bruta)
- 12 rounds ≈ 100ms en CPU moderna
- Suficiente: seguro pero no tan lento

## CÓMO EJECUTAR EJERCICIO 1

### 1. Iniciar servicios

```bash
docker-compose up -d
```

### 2. Registrar usuario

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "MyPassword123",
    "full_name": "Test User"
  }'

# Respuesta:
# {
#   "id": "uuid-123",
#   "email": "user@example.com",
#   "full_name": "Test User",
#   "is_active": true
# }
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "MyPassword123"
  }'

# Respuesta:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "user_id": "uuid-123",
#   "email": "user@example.com"
# }
```

### 4. Usar token en endpoint protegido

```bash
# Copiar el access_token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/v1/admin/metrics \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Ejecutar tests

```bash
pytest tests/test_auth_service.py -v
pytest tests/test_password.py -v
pytest tests/test_email.py -v
pytest tests/test_bcrypt.py -v
```

---

# EJERCICIO 7: MÉTRICAS

## ¿QUÉ ES?

Un sistema que recolecta y reporta métricas del sistema en tiempo real:
- Pagos procesados/fallidos
- Tasa de éxito
- Usuarios registrados
- Threads activos
- Promedio de tiempo entre pagos

## FLUJO DE FUNCIONAMIENTO

### 1. Registrar Eventos

```
AuthService.register()
   ↓
metrics.record_user_registered()  ← EVENTO
   ↓
MetricsCollector (thread-safe)
   ├─ with self._lock:  ← RLock
   │   └─ self.users_registered += 1
   └─ ✅ Sincronizado

PaymentService.process_payment()
   ↓
metrics.record_payment_processed(100.0, "USD")  ← EVENTO
   ↓
MetricsCollector (thread-safe)
   ├─ with self._lock:  ← RLock
   │   ├─ self.payments_processed += 1
   │   ├─ self.total_amount_usd += 100.0
   │   └─ self.last_payment_time = now()
   └─ ✅ Sincronizado
```

### 2. Calcular Métricas

```
GET /admin/metrics
   ↓
metrics.get_metrics()
   ↓
MetricsCollector.get_metrics()
   ├─ with self._lock:  ← RLock (lectura)
   │   ├─ uptime_seconds = (now - start).seconds
   │   ├─ success_rate = (processed / (processed + failed)) * 100
   │   ├─ avg_interval = sum(time_diffs) / len(time_diffs)
   │   └─ Construir JSON
   └─ return metrics
   
GET /admin/health
   └─ Status: "healthy"
```

## CÓDIGO IMPORTANTE

### 1. Recolector Thread-Safe (Infrastructure)

**Por qué RLock?**

```python
# app/infrastructure/concurrency/metrics_collector.py
class InMemoryMetricsCollector(MetricsCollector):
    def __init__(self):
        self._lock = threading.RLock()  # ← Reentrant Lock
        self._reset_metrics()
    
    def record_payment_processed(self, amount: float, currency: str):
        with self._lock:  # ← Sección crítica
            self.payments_processed += 1
            self.total_amount_usd += amount
            self.payment_times.append(datetime.utcnow())
            # ← Sin race condition
```

**¿Por qué RLock (Reentrant)?**
- `Lock`: Un thread no puede adquirir 2 veces
- `RLock`: Un thread SÍ puede adquirir 2+ veces
- Caso: Si A→B→A, necesitas RLock

**¿Por qué `with` statement?**
```python
# ❌ SIN with (peligroso)
self._lock.acquire()
self.payments_processed += 1  # Si excepción aquí...
self._lock.release()  # Nunca se ejecuta → DEADLOCK

# ✅ CON with (seguro)
with self._lock:
    self.payments_processed += 1  # Si excepción...
    # Siempre se libera el lock
```

### 2. Puerto (Domain)

**Por qué?** Abstraer implementación de métricas.

```python
# app/domain/ports/metrics_collector.py
class MetricsCollector(ABC):
    @abstractmethod
    def record_payment_processed(self, amount: float, currency: str):
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        pass
```

**Beneficio**: Cambiar de en-memoria a Prometheus sin tocar Domain.

### 3. Dependencia Inyectada

**Por qué?** Singleton global de métricas.

```python
# app/presentation/deps.py
_metrics_collector = InMemoryMetricsCollector()  # ← Singleton

def get_metrics_collector() -> MetricsCollector:
    return _metrics_collector  # ← Siempre la misma instancia
```

**¿Por qué Singleton?**
- Todos los servicios usan la misma
- Una única fuente de verdad
- Thread-safe centralizado

### 4. Router Protegido

**Por qué?** Solo admin puede ver métricas.

```python
# app/presentation/api/routers/metrics.py
@router.get("/admin/metrics")
async def get_metrics(
    metrics = Depends(get_metrics_collector),
    current_user = Depends(get_current_user),
    admin_verified = Depends(verify_admin)  # ← Verificación
):
    metrics_dict = metrics.get_metrics()
    return MetricsResponse(**metrics_dict)

async def verify_admin(current_user = Depends(get_current_user)):
    admin_emails = ["admin@taller.local"]
    if current_user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Not admin")
    return current_user
```

### 5. Cálculo de Métricas

**Por qué así?**

```python
def get_metrics(self) -> Dict:
    with self._lock:
        now = datetime.utcnow()
        uptime_seconds = (now - self.start_time).total_seconds()
        
        # ← Success rate
        total = self.payments_processed + self.payments_failed
        success_rate = 0.0
        if total > 0:
            success_rate = (self.payments_processed / total) * 100
        
        # ← Intervalo promedio
        avg_interval = None
        if len(self.payment_times) > 1:
            diffs = []
            for i in range(1, len(self.payment_times)):
                diff = (self.payment_times[i] - self.payment_times[i-1]).total_seconds()
                diffs.append(diff)
            if diffs:
                avg_interval = sum(diffs) / len(diffs)
        
        return {
            "uptime_seconds": uptime_seconds,
            "payments": {
                "processed": self.payments_processed,
                "success_rate_percent": round(success_rate, 2),
                "avg_interval_seconds": round(avg_interval, 2)
            }
        }
```

**¿Por qué así?**
- `total > 0`: Evitar división por cero
- `diffs` lista: Calcular promedio de diferencias
- `round()`: JSON no necesita 15 decimales

## CÓMO EJECUTAR EJERCICIO 7

### 1. Registrar usuario admin

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taller.local",
    "password": "AdminPass123"
  }'
```

### 2. Login admin

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taller.local",
    "password": "AdminPass123"
  }'

# Copiar: access_token
```

### 3. Ver métricas

```bash
TOKEN="..."

curl http://localhost:8000/api/v1/admin/metrics \
  -H "Authorization: Bearer $TOKEN"

# {
#   "payments": {
#     "processed": 0,
#     "failed": 0,
#     "success_rate_percent": 0.0,
#     "total_amount_usd": 0.0
#   },
#   "users": {"registered": 1, "logins": 1},
#   "system": {"thread_count": 8}
# }
```

### 4. Generar eventos (crear pagos)

```bash
# Ver siguiente ejercicio 9
```

### 5. Ver métricas actualizada

```bash
curl http://localhost:8000/api/v1/admin/metrics \
  -H "Authorization: Bearer $TOKEN"

# Ahora mostrará pagos procesados
```

### 6. Tests

```bash
pytest tests/test_metrics.py -v
```

---

# EJERCICIO 9: PAGOS INTERNACIONALES

## ¿QUÉ ES?

Un sistema productor-consumidor donde:
- **Productores**: Generan solicitudes de pago (threads)
- **Cola**: Almacena pagos thread-safe (max 20)
- **Consumidores (Workers)**: 3 threads que procesan pagos
- **Procesamiento**: Validación, comisión, conversión

## FLUJO DE FUNCIONAMIENTO

### 1. Crear Pago

```
POST /api/v1/payments/
{
  "merchant_id": "MERCHANT_001",
  "amount": 150.50,
  "currency": "EUR",
  "method": "card"
}
   ↓
PaymentService.create_payment()
   ├─ Validar entrada
   ├─ Crear Payment(status=PENDING)
   └─ await payment_repo.save(payment)
        ↓
        BD: INSERT INTO payments ...
   ↓
Retornar payment_id
```

### 2. Encolar para Procesamiento

```
PaymentWorkerPool.enqueue_payment(payment_id)
   ↓
self.payment_queue.put(payment_id, timeout=5)  ← Queue thread-safe
   ↓
Si cola llena → espera o error
Si éxito → payment_id en cola
```

### 3. Worker Procesa Pago

```
Worker 1/2/3
   │
   ├─ while not stop_event.is_set():
   │   │
   │   └─ payment_id = queue.get(timeout=1)  ← Bloquea esperando
   │       │
   │       ├─ Simular validación antifraude: sleep(0.2-0.8)
   │       │
   │       └─ PaymentService.process_payment(payment_id)
   │           ├─ Obtener del repo
   │           ├─ payment.mark_as_processing()
   │           │
   │           ├─ commission = calculate_commission(...)  ← 5% card
   │           ├─ amount_usd = convert_to_usd(...)        ← EUR→USD
   │           │
   │           ├─ payment.mark_as_completed(commission)
   │           ├─ await repo.update(payment)
   │           │
   │           └─ metrics.record_payment_processed(...)
   │
   └─ queue.task_done()  ← Marca como completado
```

### 4. Ejemplo Completo

```
Productor 1 ─────→ Pago: $100 EUR card
                   ↓
             Queue: [Pago 1]
                   ↓ Worker 1 agarra
             Proc: 5% comisión = $5.40
             Conv: EUR→USD: $108
             Net: $102.60
             Status: COMPLETED
             Métrica: +1 pagos

Productor 2 ─────→ Pago: ¥1000 JPY wallet
                   ↓
             Queue: [Pago 2] (esperando)
                   ↓ Worker 2 agarra
             Proc: 1% comisión = ¥10
             Conv: JPY→USD: $6.70
             Net: $6.60
             Status: COMPLETED
```

## CÓDIGO IMPORTANTE

### 1. Entidad Payment (Domain)

**Por qué?** Encapsular lógica de estado de pago.

```python
# app/domain/entities/payment.py
class Payment:
    def __init__(self, id, merchant_id, amount, currency, method, status=PENDING):
        self.id = id
        self.merchant_id = merchant_id
        self.amount = Decimal(str(amount))  # ← Decimal para dinero
        self.currency = currency
        self.method = method
        self.status = status
        self.commission = Decimal("0")
    
    def mark_as_processing(self):
        self.status = PaymentStatus.PROCESSING
    
    def mark_as_completed(self, commission: Decimal):
        self.status = PaymentStatus.COMPLETED
        self.commission = commission
    
    def mark_as_failed(self):
        self.status = PaymentStatus.FAILED
    
    def get_net_amount(self) -> Decimal:
        return self.amount - self.commission
```

**¿Por qué Decimal?**
```python
# ❌ Float (peligroso en dinero)
0.1 + 0.2 == 0.3  # False!! (0.30000000000000004)

# ✅ Decimal (preciso)
Decimal("0.1") + Decimal("0.2") == Decimal("0.3")  # True
```

**¿Por qué métodos?** No cambio directo a `status`.
```python
# ❌ Mal
payment.status = "COMPLETED"  # ¿Qué pasó con PROCESSING?

# ✅ Bien
payment.mark_as_completed(commission)  # Claro qué pasó
```

### 2. Servicio Payment (Application)

**Por qué?** Orquestar validación y cálculos.

```python
# app/application/services/payment_service.py
class PaymentService:
    COMMISSION_RATES = {
        PaymentMethod.CARD: Decimal("0.05"),              # 5%
        PaymentMethod.BANK_TRANSFER: Decimal("0.02"),    # 2%
        PaymentMethod.WALLET: Decimal("0.01")            # 1%
    }
    
    EXCHANGE_RATES = {
        "USD": Decimal("1.0"),
        "EUR": Decimal("1.08"),
        "GBP": Decimal("1.25"),
        "JPY": Decimal("0.0067")
    }
    
    def validate_payment(self, merchant_id, amount, currency, method):
        if not merchant_id:
            raise PaymentValidationException("merchant_id required")
        if amount <= 0:
            raise PaymentValidationException("amount > 0")
        if currency not in self.EXCHANGE_RATES:
            raise PaymentValidationException(f"currency not supported: {currency}")
        # ... más validaciones
    
    def calculate_commission(self, amount: Decimal, method: PaymentMethod) -> Decimal:
        rate = self.COMMISSION_RATES.get(method)
        return (amount * rate).quantize(Decimal("0.01"))
    
    def convert_to_usd(self, amount: Decimal, currency: str) -> Decimal:
        rate = self.EXCHANGE_RATES[currency]
        return (amount * rate).quantize(Decimal("0.01"))
    
    async def create_payment(self, merchant_id, amount, currency, method):
        # Validar
        self.validate_payment(merchant_id, amount, currency, method)
        
        # Crear entidad
        payment = Payment(...)
        
        # Persistir
        await self.payment_repository.save(payment)
        
        return payment
    
    async def process_payment(self, payment_id: str) -> Payment:
        payment = await self.payment_repository.find_by_id(payment_id)
        
        # Marcar procesando
        payment.mark_as_processing()
        await self.payment_repository.update(payment)
        
        try:
            # Calcular comisión
            commission = self.calculate_commission(payment.amount, payment.method)
            
            # Convertir a USD
            amount_usd = self.convert_to_usd(payment.amount, payment.currency)
            
            # Marcar completado
            payment.mark_as_completed(commission)
            await self.payment_repository.update(payment)
            
            # Registrar métrica
            self.metrics.record_payment_processed(float(amount_usd), "USD")
            
            return payment
        except Exception as e:
            payment.mark_as_failed()
            await self.payment_repository.update(payment)
            self.metrics.record_payment_failed()
            raise
```

**¿Por qué así?**
- Validar primero (fail fast)
- Crear sin persistir
- Persistir en BD
- Luego procesar
- Registrar métrica
- Manejo de errores limpio

### 3. Worker (Infrastructure)

**Por qué?** Procesamiento concurrente.

```python
# app/infrastructure/workers/payment_worker.py
class PaymentWorker(threading.Thread):
    def __init__(self, worker_id, queue, service, stop_event):
        super().__init__(daemon=True)  # ← Daemon = muere con app
        self.worker_id = worker_id
        self.queue = queue
        self.service = service
        self.stop_event = stop_event
        self.processed_count = 0
    
    def run(self):  # ← Se ejecuta en thread separado
        print(f"[{self.worker_id}] Started")
        
        while not self.stop_event.is_set():  # ← Señal de parada
            try:
                # Obtener pago (timeout para permitir check stop_event)
                payment_id = self.queue.get(timeout=1)
                
                try:
                    print(f"[{self.worker_id}] Processing {payment_id}")
                    
                    # Simular antifraude
                    time.sleep(random.uniform(0.2, 0.8))
                    
                    # Procesar (asyncio en thread)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    payment = loop.run_until_complete(
                        self.service.process_payment(payment_id)
                    )
                    
                    self.processed_count += 1
                    print(f"[{self.worker_id}] ✓ {payment_id}")
                    
                finally:
                    self.queue.task_done()  # ← Marca completado
                    
            except queue.Empty:
                continue  # ← Timeout, intenta de nuevo
        
        print(f"[{self.worker_id}] Stopped. Processed: {self.processed_count}")
```

**¿Por qué así?**
- Daemon: No bloquea cierre de app
- stop_event: Parada limpia
- timeout: No bloquea forever
- task_done: Pool sabe cuándo terminar
- try/finally: queue.task_done siempre se ejecuta

### 4. Worker Pool (Infrastructure)

**Por qué?** Gestionar múltiples workers.

```python
# app/infrastructure/workers/payment_worker.py
class PaymentWorkerPool:
    def __init__(self, num_workers, queue_size, service):
        self.payment_queue = queue.Queue(maxsize=queue_size)
        self.stop_event = threading.Event()
        self.workers = []
        
        # Crear N workers
        for i in range(num_workers):
            worker = PaymentWorker(f"Worker-{i+1}", self.payment_queue, service, self.stop_event)
            worker.start()  # ← Inicia thread
            self.workers.append(worker)
    
    def enqueue_payment(self, payment_id):
        try:
            self.payment_queue.put(payment_id, timeout=5)  # ← Bloquea si llena
        except queue.Full:
            raise RuntimeError("Queue full")
    
    def wait_all_processed(self):
        self.payment_queue.join()  # ← Bloquea hasta task_done x todo
    
    def shutdown(self, timeout=10):
        self.stop_event.set()  # ← Señal de parada
        
        for worker in self.workers:
            worker.join(timeout=timeout)  # ← Esperar fin
```

**¿Por qué así?**
- `queue.Queue(maxsize)`: Backpressure automático
- `put(timeout)`: No bloquea forever
- `join()`: Esperar a que todo termine
- `stop_event`: Parada ordenada (limpia)

### 5. Router (Presentation)

**Por qué?** HTTP ↔ Servicios.

```python
# app/presentation/api/routers/payment.py
@router.post("/", response_model=PaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    service: PaymentService = Depends(get_payment_service),
    current_user = Depends(get_current_user)
):
    try:
        payment = await service.create_payment(
            merchant_id=request.merchant_id,
            amount=request.amount,
            currency=request.currency,
            method=request.method
        )
        return PaymentResponse(
            id=payment.id,
            merchant_id=payment.merchant_id,
            amount=payment.amount,
            currency=payment.currency,
            method=payment.method.value,
            status=payment.status.value,
            commission=payment.commission,
            created_at=payment.created_at.isoformat(),
            updated_at=payment.updated_at.isoformat()
        )
    except PaymentValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
    current_user = Depends(get_current_user)
):
    payment = await service.payment_repository.find_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Not found")
    
    return PaymentStatusResponse(
        payment_id=payment.id,
        status=payment.status.value,
        amount=payment.amount,
        currency=payment.currency,
        commission=payment.commission,
        net_amount=payment.get_net_amount()
    )
```

## CÓMO EJECUTAR EJERCICIO 9

### Opción 1: Demo Automática

```bash
python demo_payment_exercise9.py
```

Genera:
- 2 productores
- 5 pagos cada uno
- 3 workers procesando
- Muestra métricas finales

### Opción 2: Manual por HTTP

```bash
# 1. Registrar user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "merchant@test.com",
    "password": "Test123Password"
  }'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "merchant@test.com",
    "password": "Test123Password"
  }' | jq -r '.access_token')

# 3. Crear pago
PAYMENT=$(curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "MERCHANT_001",
    "amount": 150.50,
    "currency": "EUR",
    "method": "card"
  }')

PAYMENT_ID=$(echo $PAYMENT | jq -r '.id')

# 4. Esperar a que worker procese (2-5 segundos)
sleep 3

# 5. Ver estado
curl -X GET http://localhost:8000/api/v1/payments/$PAYMENT_ID \
  -H "Authorization: Bearer $TOKEN"

# 6. Ver métricas admin
TOKEN_ADMIN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taller.local",
    "password": "AdminPass123"
  }' | jq -r '.access_token')

curl http://localhost:8000/api/v1/admin/metrics \
  -H "Authorization: Bearer $TOKEN_ADMIN"
```

### Tests

```bash
pytest tests/test_payment_service.py -v
```

---

# POR QUÉ ARQUITECTURA LIMPIA

## El Problema Sin Arquitectura Limpia

```python
# ❌ Todo mezclado
@app.post("/payment")
def create_payment(request, db):
    # Validación HTTP
    if not request.merchant_id:
        return {"error": "required"}
    
    # Lógica de negocio
    if request.amount <= 0:
        return {"error": "invalid"}
    
    # Cálculo de comisión
    commission = request.amount * 0.05
    
    # Acceso a BD
    db.execute("""INSERT INTO payments ...""")
    
    # Métrica
    global payments_count
    payments_count += 1  # ← RACE CONDITION!
    
    return {"id": "..."}

# Problemas:
# 1. ¿Cómo testeo sin BD?
# 2. ¿Cómo cambio de SQLAlchemy a MongoDB?
# 3. ¿Cómo reutilizo lógica en otro endpoint?
# 4. ¿Qué pasa si falla la BD en el medio?
# 5. Métrica sin thread-safety → datos corruptos
```

## La Solución: Arquitectura Limpia

```
Domain (puro, testeable)
   ├─ class Payment → Entidad
   ├─ validate_payment() → Lógica
   └─ payment.commission → Cálculo

Application (orquestador)
   └─ PaymentService.create_payment() → Coordina

Infrastructure (implementaciones)
   ├─ PaymentRepository → Dónde guardar
   └─ MetricsCollector → Cómo registrar

Presentation (HTTP)
   └─ @router.post("/payment") → Traducir

Beneficios:
✅ Testeable: cada parte sin dependencias
✅ Flexible: cambiar BD/métrica sin tocar lógica
✅ Mantenible: responsabilidades claras
✅ Escalable: agregar features fácil
```

## Ejemplo: Cambiar de BD

### Opción 1: SQLAlchemy (Actual)

```python
class PaymentRepositorySQLAlchemy(PaymentRepository):
    async def save(self, payment):
        db_payment = PaymentModel(...)
        db.add(db_payment)
        db.commit()
```

### Opción 2: MongoDB (Futuro)

```python
class PaymentRepositoryMongoDB(PaymentRepository):
    async def save(self, payment):
        await self.mongo_db.payments.insert_one({
            "_id": payment.id,
            "merchant_id": payment.merchant_id,
            ...
        })
```

### En Dependencias (Presentation)

```python
# ❌ Acoplado a SQLAlchemy
def get_payment_service():
    return PaymentService(PaymentRepositorySQLAlchemy(db))

# ✅ Abstraído a interface
def get_payment_service(
    repository: PaymentRepository = Depends(get_payment_repository)
):
    return PaymentService(repository)

# En config:
USE_MONGODB = True  # Cambiar fácil
if USE_MONGODB:
    def get_payment_repository():
        return PaymentRepositoryMongoDB(mongo_client)
else:
    def get_payment_repository():
        return PaymentRepositorySQLAlchemy(sql_db)
```

**Beneficio**: Cambiar BD sin tocar `PaymentService`.

---

# CÓMO MODULARIZAMOS

## Estructura por Capas

```
Domain/                           ← 0 dependencias externas
  entities/                       ← Objetos de negocio
    - user.py
    - payment.py
  value_objects/                  ← Valores con validación
    - email.py
    - password.py
  ports/                          ← Interfaces (contratos)
    - user_repository.py
    - payment_repository.py
    - metrics_collector.py
  exceptions.py                   ← Errores de dominio
  constants.py                    ← Enums

Application/                      ← Depende solo de Domain
  services/
    - auth_service.py             ← Orquestra Domain + Puertos
    - payment_service.py
    - jwt_service.py

Infrastructure/                   ← Depende de Domain + Application
  database/
    - models.py                   ← Mapeo BD
    - repository_sqlalchemy.py    ← Implementa Puerto
  security/
    - bcrypt_hasher.py            ← Implementa Puerto
  workers/
    - payment_worker.py           ← Threading
  concurrency/
    - metrics_collector.py        ← Implementa Puerto (thread-safe)

Presentation/                     ← Depende de todo
  api/
    routers/
      - auth.py                   ← Endpoints
      - payment.py
      - metrics.py
  schemas/                        ← DTOs (Pydantic)
    - auth.py
    - payment.py
  deps.py                         ← Inyección (FastAPI)

Tests/                            ← Todo testeable
  test_auth_service.py
  test_payment_service.py
  test_metrics.py
```

## Flujo de Dependencias

```
Presentation
    ↓ (depende)
Application
    ↓ (depende)
Domain
    ↑ (NO depende de nada)
```

**Regla de oro**: Las flechas siempre apuntan hacia adentro.

## Beneficio de Modularización

```
Cambiar comportamiento de autenticación:
  1. Modificar Domain: auth_service.py
  2. ✓ No toca: BD, HTTP, Workers
  
Agregar nuevo tipo de repo:
  1. Crear: repositories/payment_repository_mongodb.py
  2. Implementar: PaymentRepository
  3. Registrar en: deps.py
  4. ✓ No toca: Servicios, Dominio

Cambiar algoritmo de hash:
  1. Crear: security/argon2_hasher.py
  2. Implementar: PasswordHasher
  3. Registrar en: deps.py
  4. ✓ No toca: Domain, Auth logic
```

---

# CÓMO EJECUTAR TODO

## 1. Instalar Docker

```bash
# Windows: Descargar Docker Desktop
# Mac: brew install docker-desktop
# Linux: apt install docker.io docker-compose
```

## 2. Clonar/Descargar Proyecto

```bash
cd "c:\Users\JUAN ZULUAGA\Desktop\ACS\Taller Final"
```

## 3. Iniciar

```bash
docker-compose up -d
```

## 4. Verificar

```bash
docker-compose ps

# Debería ver:
# taller_final_db      ✓ postgres UP
# taller_final_app     ✓ app UP
```

## 5. Acceder

- **API**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs
- **Logs**: `docker-compose logs -f app`

## 6. Tests

```bash
docker-compose exec app pytest tests/ -v
```

## 7. Demo

```bash
docker-compose exec app python demo_payment_exercise9.py
```

## 8. Detener

```bash
docker-compose down
```

---

# RESUMEN EJECUTIVO

| Aspecto | Ejercicio 1 | Ejercicio 7 | Ejercicio 9 |
|---------|------------|-----------|-----------|
| **Qué es** | Autenticación JWT | Métricas | Pagos |
| **Patrón** | Value Objects | Singleton + RLock | Productor-Consumidor |
| **Thread-Safe** | Bcrypt hash | RLock | Queue thread-safe |
| **Testeable** | Sí (mocks) | Sí (mocks) | Sí (mocks) |
| **Escalable** | Sí | Sí | Sí (N workers) |
| **Arquitectura** | Limpia (4 capas) | Limpia (4 capas) | Limpia (4 capas) |

Todos los ejercicios siguen **Arquitectura Limpia**:
- Domain: Lógica pura
- Application: Orquestación
- Infrastructure: Implementaciones
- Presentation: HTTP

**Resultado**: Código testeable, flexible, mantenible, escalable.

---

**Última actualización**: Enero 2024
**Estado**: ✅ Completo y funcional
