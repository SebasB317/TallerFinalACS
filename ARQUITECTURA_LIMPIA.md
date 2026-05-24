# Guía de Arquitectura Limpia - Taller Final

## 📐 Principios de la Arquitectura Limpia

### 1. Independencia de Frameworks

La lógica de negocio NO depende de FastAPI, SQLAlchemy, etc.

```python
# ❌ INCORRECTO - Lógica en el router
@router.post("/users")
async def create_user(req: CreateUserRequest, db: Session):
    user = User(email=req.email, password=req.password)
    db.add(user)
    db.commit()
    return user

# ✅ CORRECTO - Lógica en servicio
class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo
    
    async def register(self, email, password):
        user = User(email, hashed_password)
        await self.repo.save(user)
        return user
```

### 2. Independencia de la Base de Datos

El dominio NO sabe cómo se persisten los datos.

```python
# ❌ INCORRECTO - User importa SQLAlchemy
from sqlalchemy import Column, String

class User:
    __tablename__ = "users"
    email = Column(String(255))

# ✅ CORRECTO - User es una clase Python pura
class User:
    def __init__(self, id, email, hashed_password):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password

# Persistencia separada
class UserRepositorySQLAlchemy(UserRepository):
    def save(self, user: User):
        db_user = UserModel(...)
        db.add(db_user)
```

### 3. Testeable

Cada capa puede testearse sin las otras.

```python
# Test de dominio - Sin BD ni HTTP
def test_password_validation():
    with pytest.raises(InvalidPasswordException):
        Password("weak")

# Test de servicio - Con mock de repo
@pytest.mark.asyncio
async def test_register():
    repo_mock = Mock()
    auth = AuthService(repo_mock, hasher, metrics)
    user = await auth.register("user@test.com", "Pass123")
    repo_mock.save.assert_called_once()

# Test de API - Con test client
def test_register_endpoint():
    response = client.post("/api/v1/auth/register", json={...})
    assert response.status_code == 201
```

### 4. Inversión de Control

Los servicios reciben sus dependencias, no las crean.

```python
# ❌ INCORRECTO - Crear dependencias internas
class AuthService:
    def __init__(self):
        self.repo = UserRepositorySQLAlchemy()  # Acoplado
        self.hasher = BcryptHasher()

# ✅ CORRECTO - Inyección de dependencias
class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        metrics_collector: MetricsCollector
    ):
        self.repo = user_repository  # Polimórfico
        self.hasher = password_hasher
        self.metrics = metrics_collector
```

## 🏗️ Flujo de Datos

### Entrada (Request)

```
HTTP Request
    ↓
FastAPI Router (presentation/api/routers/auth.py)
    ↓ Mapea a DTO (pydantic)
Request DTO (RegisterRequest)
    ↓ Extrae datos
AuthService.register(email, password)
    ↓ Crea Value Objects
Email(email), Password(password)
    ↓ Valida
User(id, email, hashed_password)
    ↓ Crea entidad
UserRepository.save(user)
    ↓ Persiste en BD
UserRepositorySQLAlchemy → SQLAlchemy → PostgreSQL
    ↓ Retorna
UserResponse DTO → JSON → HTTP 201 Created
```

### Dependencias

```
Domain (no depende de nada)
    ↑
Application (depende solo de Domain)
    ↑
Infrastructure (depende de Domain y Application)
    ↑
Presentation (depende de todas)
```

**Regla de oro**: Las flechas de dependencia siempre apuntan hacia adentro (hacia el Domain).

## 🔌 Puertos (Interfaces)

Define contratos que puede implementar cualquiera.

```python
# Puerto (interfaz de dominio)
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None:
        pass

# Adaptador 1 - SQLAlchemy
class UserRepositorySQLAlchemy(UserRepository):
    async def save(self, user: User):
        # Implementación con BD

# Adaptador 2 - Memoria (para tests)
class UserRepositoryMemory(UserRepository):
    async def save(self, user: User):
        # Implementación en memoria

# Adaptador 3 - MongoDB (futuro)
class UserRepositoryMongoDB(UserRepository):
    async def save(self, user: User):
        # Implementación con MongoDB
```

**Beneficio**: Cambiar de BD sin modificar el dominio.

## 🎯 Value Objects vs Entidades

### Value Objects

- Identificables solo por sus valores
- Inmutables
- Sin identidad propia
- Validados en construcción

```python
class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise InvalidEmailException()
        self.value = value.lower()
    
    def __eq__(self, other):
        return self.value == other.value
```

### Entidades

- Tienen identidad única (ID)
- Pueden cambiar de estado
- Encapsulan lógica de negocio
- Raíz del agregado

```python
class User:
    def __init__(self, id, email, hashed_password):
        self.id = id  # Identidad
        self.email = email
        self.hashed_password = hashed_password
    
    def deactivate(self):
        self.is_active = False
```

## 🔒 Seguridad en Capas

### Domain
```python
class Password(ValueObject):
    # Valida contraseña
    # Min 8 chars, mayúscula, número
```

### Application
```python
class AuthService:
    def authenticate(self, email, password):
        # Verifica contraseña con hasher
        hasher.verify(password, user.hashed_password)
```

### Infrastructure
```python
class BcryptHasher:
    def hash(self, password):
        # Bcrypt 12 rounds
        return bcrypt.hashpw(password, salt)
```

### Presentation
```python
@router.post("/login")
async def login(req: LoginRequest):
    # Valida formato JSON
    # Retorna JWT
```

## 🧮 Ejemplo: Ejercicio 9 (Pagos)

### 1. Domain (Lógica Pura)

```python
# Entidades
class Payment:
    def mark_as_processing(self):
        self.status = PaymentStatus.PROCESSING
    
    def mark_as_completed(self, commission):
        self.commission = commission
        self.status = PaymentStatus.COMPLETED

# Puertos
class PaymentRepository(ABC):
    @abstractmethod
    async def save(self, payment: Payment):
        pass
```

### 2. Application (Orquestación)

```python
class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        metrics_collector: MetricsCollector
    ):
        self.repo = payment_repository
        self.metrics = metrics_collector
    
    async def process_payment(self, payment_id):
        payment = await self.repo.find_by_id(payment_id)
        payment.mark_as_processing()
        
        try:
            commission = self.calculate_commission(...)
            payment.mark_as_completed(commission)
            self.metrics.record_payment_processed(...)
        except Exception:
            payment.mark_as_failed()
            self.metrics.record_payment_failed()
```

### 3. Infrastructure (Implementaciones)

```python
# Persistencia
class PaymentRepositorySQLAlchemy(PaymentRepository):
    async def save(self, payment: Payment):
        db_payment = PaymentModel(...)
        db.add(db_payment)
        db.commit()

# Workers concurrentes
class PaymentWorker(threading.Thread):
    def run(self):
        while not self.stop_event.is_set():
            payment_id = self.queue.get()
            asyncio.run(
                self.payment_service.process_payment(payment_id)
            )
```

### 4. Presentation (HTTP)

```python
@router.post("/api/v1/payments/")
async def create_payment(
    req: CreatePaymentRequest,
    service: PaymentService = Depends(get_payment_service)
):
    payment = await service.create_payment(...)
    return PaymentResponse.from_entity(payment)
```

## 🎪 Inyección de Dependencias

### Sin FastAPI

```python
# Manual
hasher = BcryptHasher()
user_repo = UserRepositorySQLAlchemy(db)
metrics = InMemoryMetricsCollector()
auth_service = AuthService(user_repo, hasher, metrics)

user = await auth_service.register("user@test.com", "Pass123")
```

### Con FastAPI

```python
# Funciones de dependencia
def get_password_hasher():
    return BcryptHasher()

def get_auth_service(
    hasher = Depends(get_password_hasher),
    repo = Depends(get_user_repository)
):
    return AuthService(repo, hasher, metrics)

# En router
@router.post("/register")
async def register(
    req: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register(req.email, req.password)
```

**FastAPI resuelve automáticamente el árbol de dependencias.**

## 🧪 Testing en Capas

### Test de Domain (Rápido, sin dependencias)

```python
def test_email_validation():
    email = Email("valid@example.com")
    assert email.value == "valid@example.com"
    
    with pytest.raises(InvalidEmailException):
        Email("invalid")
```

### Test de Application (Con mocks)

```python
@pytest.mark.asyncio
async def test_payment_processing():
    repo_mock = Mock()
    metrics_mock = Mock()
    
    service = PaymentService(repo_mock, metrics_mock)
    
    # Setup
    repo_mock.find_by_id.return_value = Payment(...)
    
    # Act
    await service.process_payment("payment_id")
    
    # Assert
    repo_mock.update.assert_called_once()
    metrics_mock.record_payment_processed.assert_called_once()
```

### Test de Infrastructure (Integración)

```python
@pytest.fixture
def db():
    # BD de test
    return SessionLocal()

def test_save_user(db):
    repo = UserRepositorySQLAlchemy(db)
    user = User(id="1", email="test@example.com", hashed_password="...")
    
    repo.save(user)
    
    result = repo.find_by_id("1")
    assert result.email == "test@example.com"
```

### Test de Presentation (E2E)

```python
def test_register_endpoint(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "MyPassword123"
        }
    )
    
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"
```

## 📋 Checklist de Arquitectura Limpia

- [ ] Domain no importa nada de la app (solo stdlib)
- [ ] Application solo importa Domain
- [ ] Infrastructure importa Domain y Application
- [ ] Presentation importa Application (vía dependencias)
- [ ] Cada clase tiene una única responsabilidad
- [ ] Las dependencias apuntan hacia adentro (al Domain)
- [ ] Puertos (interfaces) para cambiar implementaciones
- [ ] Tests para cada capa de forma independiente
- [ ] DTOs separados de entidades
- [ ] Validación en Domain (Value Objects)
- [ ] Seguridad distribuida en capas
- [ ] Errores de dominio vs errores técnicos

## 🚀 Beneficios Conseguidos

✅ **Testeable**: Cada capa sin dependencias de la otra
✅ **Flexible**: Cambiar BD, framework, sin tocar lógica
✅ **Mantenible**: Código organizado, responsabilidades claras
✅ **Escalable**: Agregar features sin romper existentes
✅ **Independiente**: No acoplado a frameworks
✅ **Profesional**: Sigue estándares de la industria

---

**Recuerda**: La Arquitectura Limpia no es sobre código, es sobre decisiones de diseño que **facilitan el cambio futuro**.
