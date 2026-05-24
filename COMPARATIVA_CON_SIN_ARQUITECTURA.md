# 📊 COMPARATIVA: CON vs SIN ARQUITECTURA LIMPIA

## Ejercicio 1: Autenticación

### ❌ SIN Arquitectura Limpia (Monolítica)

```python
# routes/auth.py - TODO EN UN ARCHIVO
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import jwt

router = APIRouter()

@router.post("/register")
def register(email: str, password: str, db: Session):
    # Validación email (inline)
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise HTTPException(status_code=400, detail="Email inválido")
    
    # Validación password (inline)
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password muy corto")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Sin mayúscula")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Sin número")
    
    # Verificar existe (inline)
    existing = db.query(UserModel).filter(UserModel.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email existe")
    
    # Hash (inline)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode(), salt).decode()
    
    # Crear y guardar (inline)
    user = UserModel(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hashed
    )
    db.add(user)
    db.commit()
    
    # Retornar
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active
    }

@router.post("/login")
def login(email: str, password: str, db: Session):
    # Validación email (repetida)
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise HTTPException(status_code=400, detail="Email inválido")
    
    # Buscar (inline)
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Verificar password (inline)
    if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Generar JWT (inline)
    payload = {
        "sub": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, "SECRET", algorithm="HS256")
    
    # Retornar
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id
    }

# PROBLEMAS:
# ❌ Validación duplicada (email en 2 lugares)
# ❌ Lógica mezclada (HTTP + BD + Seguridad)
# ❌ Difícil testear sin BD
# ❌ Difícil cambiar de BD
# ❌ No reutilizable
# ❌ Acoplado a FastAPI
```

**Problemas:**

1. **Validación duplicada**: Email se valida igual en 2 endpoints
2. **Lógica espageti**: HTTP, BD, seguridad todo junto
3. **No testeable**: ¿Cómo testeo sin BD?
4. **Acoplado a frameworks**: Si cambio a Flask, reescribir todo
5. **Difícil cambiar**: ¿Cambiar de SQLAlchemy? Toca todo

### ✅ CON Arquitectura Limpia (Modular)

```python
# domain/value_objects/email.py
class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise InvalidEmailException(f"Email inválido: {value}")
        self.value = value.lower()
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# domain/value_objects/password.py
class Password:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise InvalidPasswordException("Min 8, mayúscula, número")
        self.value = value
    
    @staticmethod
    def _is_valid(password: str) -> bool:
        return (len(password) >= 8 and 
                re.search(r'[A-Z]', password) and 
                re.search(r'\d', password))

# domain/entities/user.py
class User:
    def __init__(self, id, email, hashed_password):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password

# domain/ports/user_repository.py
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User): pass
    
    @abstractmethod
    async def find_by_email(self, email: str): pass

# application/services/auth_service.py
class AuthService:
    def __init__(self, repo: UserRepository, hasher: PasswordHasher):
        self.repo = repo
        self.hasher = hasher
    
    async def register(self, email: str, password: str) -> User:
        # 1. Validar Value Objects
        email_vo = Email(email)  # Falla si inválido
        password_vo = Password(password)
        
        # 2. Verificar regla de negocio
        if await self.repo.find_by_email(email_vo.value):
            raise UserAlreadyExistsException()
        
        # 3. Crear entidad
        user = User(
            id=str(uuid.uuid4()),
            email=email_vo.value,
            hashed_password=self.hasher.hash(password_vo.value)
        )
        
        # 4. Persistir
        await self.repo.save(user)
        return user

# infrastructure/repositories/user_repository_sqlalchemy.py
class UserRepositorySQLAlchemy(UserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, user: User):
        db_user = UserModel(...)
        self.db.add(db_user)
        self.db.commit()

# infrastructure/security/bcrypt_hasher.py
class BcryptHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return bcrypt.hashpw(...).decode()

# presentation/api/routers/auth.py
@router.post("/register")
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.register(request.email, request.password)
        return UserResponse.from_entity(user)
    except InvalidEmailException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
```

**Beneficios:**

✅ **Validación centralizada**: Un lugar (Email VO)
✅ **Lógica separada**: Domain no conoce HTTP
✅ **Testeable**: Testear `Email`, `AuthService` sin BD
✅ **Flexible**: Cambiar repo, hasher sin tocar lógica
✅ **Reutilizable**: `Email` usado en muchos lugares

---

## Ejercicio 7: Métricas

### ❌ SIN Arquitectura Limpia

```python
# routes/admin.py
global_payments_processed = 0  # ← PROBLEMA: Global mutable
global_users_registered = 0

@router.post("/payment")
def create_payment(..., db: Session):
    # ... crear pago ...
    global_payments_processed += 1  # ← RACE CONDITION!
    # Si 2 threads ejecutan aquí al mismo tiempo:
    # Thread 1: Lee 10, escribe 11
    # Thread 2: Lee 10, escribe 11
    # Resultado: 11 en lugar de 12 ❌

@router.post("/register")
def register(..., db: Session):
    # ... crear user ...
    global_users_registered += 1  # ← RACE CONDITION!

@router.get("/metrics")
def get_metrics():
    return {
        "payments": global_payments_processed,
        "users": global_users_registered
    }
```

**Problemas:**

- ❌ Race condition (global mutable)
- ❌ No thread-safe
- ❌ Métrica puede estar corrompida
- ❌ Difícil debuggear

### ✅ CON Arquitectura Limpia

```python
# domain/ports/metrics_collector.py
class MetricsCollector(ABC):
    @abstractmethod
    def record_payment_processed(self, amount: float): pass
    
    @abstractmethod
    def get_metrics(self) -> Dict: pass

# infrastructure/concurrency/metrics_collector.py
class InMemoryMetricsCollector(MetricsCollector):
    def __init__(self):
        self._lock = threading.RLock()  # ← SINCRONIZACIÓN
        self.payments_processed = 0
    
    def record_payment_processed(self, amount: float):
        with self._lock:  # ← SECCIÓN CRÍTICA
            self.payments_processed += 1
            # Thread 1 y 2 nunca compiten

    def get_metrics(self) -> Dict:
        with self._lock:  # ← LECTURA SEGURA
            return {"payments": self.payments_processed}

# application/services/payment_service.py
class PaymentService:
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
    
    async def process_payment(self, payment_id):
        # ... procesar ...
        self.metrics.record_payment_processed(100.0)  # ← SEGURO

# presentation/api/routers/payment.py
@router.get("/metrics")
async def get_metrics(
    metrics: MetricsCollector = Depends(get_metrics_collector),
    current_user = Depends(verify_admin)
):
    return metrics.get_metrics()
```

**Beneficios:**

✅ **Thread-safe**: RLock previene race conditions
✅ **Separado**: Servicios no saben de threading
✅ **Testeable**: Mock de MetricsCollector
✅ **Flexible**: Cambiar de en-memoria a Prometheus
✅ **Observable**: Métricas siempre correctas

---

## Ejercicio 9: Pagos Internacionales

### ❌ SIN Arquitectura Limpia

```python
# routes/payment.py
from sqlalchemy.orm import Session
import queue

payment_queue = queue.Queue(maxsize=20)  # ← Global

@router.post("/payments")
def create_payment(request, db: Session):
    # Validación inline
    if request.amount <= 0:
        raise HTTPException(...)
    
    # Crear en BD inline
    db_payment = PaymentModel(...)
    db.add(db_payment)
    db.commit()
    
    # Encolar inline
    try:
        payment_queue.put(db_payment.id, timeout=5)
    except queue.Full:
        raise HTTPException(...)
    
    return {"id": db_payment.id}

# workers/payment_worker.py (separado)
import threading

class PaymentWorker(threading.Thread):
    def run(self):
        while True:
            payment_id = payment_queue.get()
            
            # Obtener de BD
            db = SessionLocal()
            payment = db.query(PaymentModel).filter_by(id=payment_id).first()
            
            # Procesamiento inline
            if payment.method == "card":
                commission = payment.amount * 0.05
            elif payment.method == "bank":
                commission = payment.amount * 0.02
            else:
                commission = payment.amount * 0.01
            
            # Conversión inline
            if payment.currency == "EUR":
                amount_usd = payment.amount * 1.08
            elif payment.currency == "GBP":
                amount_usd = payment.amount * 1.25
            else:
                amount_usd = payment.amount
            
            # Actualizar BD
            payment.status = "COMPLETED"
            payment.commission = commission
            db.commit()

# main.py
workers = [PaymentWorker() for _ in range(3)]
for w in workers:
    w.start()
```

**Problemas:**

- ❌ Lógica espageti (validación, conversión, etc)
- ❌ Difícil testear (acoplado a BD, threading)
- ❌ Duplicación (commission en 2 lugares)
- ❌ Difícil cambiar (tasas hardcodeadas)
- ❌ Sin manejo de errores

### ✅ CON Arquitectura Limpia

```python
# domain/entities/payment.py
class Payment:
    def __init__(self, id, merchant_id, amount, currency, method):
        self.id = id
        self.amount = Decimal(str(amount))
        self.currency = currency
        self.method = method
        self.status = PaymentStatus.PENDING
    
    def mark_as_processing(self):
        self.status = PaymentStatus.PROCESSING
    
    def mark_as_completed(self, commission: Decimal):
        self.commission = commission
        self.status = PaymentStatus.COMPLETED

# domain/ports/payment_repository.py
class PaymentRepository(ABC):
    @abstractmethod
    async def save(self, payment: Payment): pass
    
    @abstractmethod
    async def find_by_id(self, payment_id: str): pass
    
    @abstractmethod
    async def update(self, payment: Payment): pass

# application/services/payment_service.py
class PaymentService:
    COMMISSION_RATES = {
        "card": Decimal("0.05"),
        "bank": Decimal("0.02"),
        "wallet": Decimal("0.01")
    }
    
    EXCHANGE_RATES = {
        "USD": Decimal("1.0"),
        "EUR": Decimal("1.08"),
        "GBP": Decimal("1.25")
    }
    
    def __init__(self, repo: PaymentRepository, metrics: MetricsCollector):
        self.repo = repo
        self.metrics = metrics
    
    def calculate_commission(self, amount, method):
        rate = self.COMMISSION_RATES.get(method)
        return (amount * rate).quantize(Decimal("0.01"))
    
    def convert_to_usd(self, amount, currency):
        rate = self.EXCHANGE_RATES[currency]
        return (amount * rate).quantize(Decimal("0.01"))
    
    async def create_payment(self, merchant_id, amount, currency, method):
        if amount <= 0:
            raise PaymentValidationException()
        
        payment = Payment(str(uuid.uuid4()), merchant_id, amount, currency, method)
        await self.repo.save(payment)
        return payment
    
    async def process_payment(self, payment_id):
        payment = await self.repo.find_by_id(payment_id)
        payment.mark_as_processing()
        await self.repo.update(payment)
        
        try:
            commission = self.calculate_commission(payment.amount, payment.method)
            amount_usd = self.convert_to_usd(payment.amount, payment.currency)
            
            payment.mark_as_completed(commission)
            await self.repo.update(payment)
            
            self.metrics.record_payment_processed(float(amount_usd), "USD")
            return payment
        except Exception:
            payment.mark_as_failed()
            await self.repo.update(payment)
            self.metrics.record_payment_failed()
            raise

# infrastructure/workers/payment_worker.py
class PaymentWorker(threading.Thread):
    def __init__(self, worker_id, queue, service, stop_event):
        super().__init__()
        self.worker_id = worker_id
        self.queue = queue
        self.service = service
        self.stop_event = stop_event
    
    def run(self):
        while not self.stop_event.is_set():
            try:
                payment_id = self.queue.get(timeout=1)
                asyncio.run(self.service.process_payment(payment_id))
            except queue.Empty:
                continue

# presentation/api/routers/payment.py
@router.post("/payments/")
async def create_payment(
    request: CreatePaymentRequest,
    service: PaymentService = Depends(get_payment_service),
    worker_pool: PaymentWorkerPool = Depends(get_worker_pool),
    current_user = Depends(get_current_user)
):
    try:
        payment = await service.create_payment(...)
        worker_pool.enqueue_payment(payment.id)
        return PaymentResponse.from_entity(payment)
    except PaymentValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Beneficios:**

✅ **Lógica centralizada**: `calculate_commission`, `convert_to_usd`
✅ **Testeable**: Mock de repo, no necesita threading
✅ **Flexible**: Cambiar tasas sin tocar código
✅ **Reutilizable**: Métodos usados en múltiples lugares
✅ **Manejo de errores**: Try/except limpio
✅ **Escalable**: N workers fácil

---

## Comparativa de Testabilidad

### ❌ SIN Arquitectura (Imposible testear)

```python
def test_create_payment():
    # ¿Cómo testeo sin base de datos?
    # ¿Cómo testeo sin workers?
    # ¿Cómo testeo sin FastAPI?
    # No se puede ❌
```

### ✅ CON Arquitectura (Fácil testear)

```python
def test_calculate_commission():
    service = PaymentService(Mock(), Mock())
    commission = service.calculate_commission(Decimal("100"), "card")
    assert commission == Decimal("5.00")

def test_convert_to_usd():
    service = PaymentService(Mock(), Mock())
    usd = service.convert_to_usd(Decimal("100"), "EUR")
    assert usd == Decimal("108.00")

@pytest.mark.asyncio
async def test_create_payment():
    repo_mock = Mock()
    metrics_mock = Mock()
    service = PaymentService(repo_mock, metrics_mock)
    
    payment = await service.create_payment("M1", Decimal("100"), "USD", "card")
    
    assert payment.id is not None
    repo_mock.save.assert_called_once()

@pytest.mark.asyncio
async def test_process_payment():
    repo_mock = Mock()
    repo_mock.find_by_id.return_value = Payment(...)
    metrics_mock = Mock()
    service = PaymentService(repo_mock, metrics_mock)
    
    payment = await service.process_payment("payment-123")
    
    assert payment.status == PaymentStatus.COMPLETED
    repo_mock.update.assert_called_once()
    metrics_mock.record_payment_processed.assert_called_once()
```

---

## Resumen: Por Qué Arquitectura Limpia

| Aspecto | Sin Arquitectura | Con Arquitectura |
|---------|-----------------|-----------------|
| **Linajes de código** | Centenas en 1 archivo | Decenas en múltiples |
| **Testabilidad** | Imposible | Fácil |
| **Reusabilidad** | No (acoplado) | Sí (módulos) |
| **Flexibilidad** | Cambiar = reescribir | Cambiar = plugear |
| **Mantenibilidad** | Pesadilla | Placer |
| **Escalabilidad** | Limitada | Ilimitada |
| **Tiempo para bugs** | Horas (messy) | Minutos (claro) |
| **Tiempo para features** | Días (temeroso) | Horas (seguro) |

---

## La Metáfora

**Sin Arquitectura Limpia** = Casa sin planos
- Todo en un cuarto
- Difícil encontrar cosas
- Imposible agregar cuartos
- Una reparación rompe todo

**Con Arquitectura Limpia** = Casa con planos
- Cuartos bien separados
- Fácil encontrar/cambiar
- Agregar cuartos es simple
- Una reparación ≠ afecta otros

---

**Conclusión**: Arquitectura Limpia no es lujo, es **necesidad** para código profesional.
