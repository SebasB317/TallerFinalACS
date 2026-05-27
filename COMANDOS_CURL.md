# 🔧 COMANDOS CURL LISTOS PARA COPIAR

**Usa estos comandos directamente en PowerShell o Bash**

---

## EJERCICIO 1: AUTENTICACIÓN JWT

### 1️⃣ Registrar Usuario
```bash
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "juan@example.com",
    "password": "Password123",
    "full_name": "Juan Zuluaga"
  }'
```

**En Linux/Mac (sin backticks):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@example.com","password":"Password123","full_name":"Juan Zuluaga"}'
```

---

### 2️⃣ Intentar Email Inválido (Debe fallar con 422)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "invalid-email",
    "password": "Password123"
  }'
```

---

### 3️⃣ Intentar Contraseña sin Número (Debe fallar con 422)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "NoNumeros"
  }'
```

---

### 4️⃣ Login y Obtener Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "juan@example.com",
    "password": "Password123"
  }'
```

**Respuesta (COPIA el access_token):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 5️⃣ Acceder Endpoint sin Token (Debe retornar 401)
```bash
curl -X GET http://localhost:8000/api/v1/admin/metrics
```

---

### 6️⃣ Acceder Endpoint CON Token (Debe retornar 200)
```bash
curl -X GET http://localhost:8000/api/v1/admin/metrics `
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## EJERCICIO 7: DASHBOARD ADMINISTRATIVO

### 1️⃣ Registrar Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123",
    "full_name": "Administrador"
  }'
```

---

### 2️⃣ Login Admin (COPIA el token)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123"
  }'
```

---

### 3️⃣ Ver Métricas como Admin
```bash
curl -X GET http://localhost:8000/api/v1/admin/metrics `
  -H "Authorization: Bearer <admin-token-aqui>"
```

**Respuesta esperada (200 OK con métricas):**
```json
{
  "timestamp": "2026-05-27T03:30:00",
  "uptime_seconds": 125.5,
  "payments": {
    "processed": 15,
    "failed": 0,
    "total": 15,
    "success_rate_percent": 100.0,
    "total_amount_usd": 2500.00
  },
  "users": {
    "registered": 2,
    "logins": 2
  }
}
```

---

### 4️⃣ Registrar Usuario Normal
```bash
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "user@example.com",
    "password": "UserPass123",
    "full_name": "Usuario Normal"
  }'
```

---

### 5️⃣ Login Usuario Normal (COPIA el token)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "user@example.com",
    "password": "UserPass123"
  }'
```

---

### 6️⃣ Usuario Normal Intenta Acceder Métricas (Debe retornar 403)
```bash
curl -X GET http://localhost:8000/api/v1/admin/metrics `
  -H "Authorization: Bearer <user-token-aqui>"
```

**Respuesta esperada (403 Forbidden):**
```json
{
  "detail": "Solo administradores pueden acceder a métricas"
}
```

---

## EJERCICIO 9: PAGOS INTERNACIONALES

### 1️⃣ Crear Pago en USD
```bash
curl -X POST http://localhost:8000/api/v1/payments/ `
  -H "Authorization: Bearer <juan-token>" `
  -H "Content-Type: application/json" `
  -d '{
    "merchant_id": "MERCHANT_001",
    "amount": 100.00,
    "currency": "USD",
    "method": "card"
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": "payment-uuid-1",
  "merchant_id": "MERCHANT_001",
  "amount": 100.0,
  "currency": "USD",
  "method": "card",
  "status": "pending",
  "commission": 0,
  "created_at": "2026-05-27T03:30:00"
}
```

**IMPORTANTE: COPIA el `id` para la siguiente prueba**

---

### 2️⃣ Crear Pago en EUR
```bash
curl -X POST http://localhost:8000/api/v1/payments/ `
  -H "Authorization: Bearer <juan-token>" `
  -H "Content-Type: application/json" `
  -d '{
    "merchant_id": "MERCHANT_002",
    "amount": 150.50,
    "currency": "EUR",
    "method": "card"
  }'
```

---

### 3️⃣ Crear Pago en GBP con Bank Transfer
```bash
curl -X POST http://localhost:8000/api/v1/payments/ `
  -H "Authorization: Bearer <juan-token>" `
  -H "Content-Type: application/json" `
  -d '{
    "merchant_id": "MERCHANT_003",
    "amount": 200.00,
    "currency": "GBP",
    "method": "bank_transfer"
  }'
```

---

### 4️⃣ Esperar 3 segundos (Workers procesando)
```bash
Start-Sleep -Seconds 3
```

---

### 5️⃣ Obtener Estado del Pago Procesado
```bash
curl -X GET "http://localhost:8000/api/v1/payments/<payment-id-aqui>" `
  -H "Authorization: Bearer <juan-token>"
```

**Respuesta esperada (200 OK):**
```json
{
  "payment_id": "payment-uuid-1",
  "status": "completed",
  "amount": 100.0,
  "currency": "USD",
  "method": "card",
  "commission": 5.0,
  "net_amount": 95.0,
  "amount_usd": 100.0,
  "exchange_rate": 1.0
}
```

---

### 6️⃣ Obtener Todos los Pagos
```bash
curl -X GET http://localhost:8000/api/v1/payments/ `
  -H "Authorization: Bearer <juan-token>"
```

**Respuesta esperada (200 OK):**
```json
{
  "payments": [
    {
      "payment_id": "uuid-1",
      "status": "completed",
      "amount": 100.0,
      "currency": "USD"
    },
    {
      "payment_id": "uuid-2",
      "status": "completed",
      "amount": 150.50,
      "currency": "EUR"
    }
  ]
}
```

---

## TESTS UNITARIOS

### Ejecutar todos los tests
```bash
docker-compose exec -T app pytest tests/ -v
```

**Resultado esperado:**
```
tests/test_auth.py::test_register_user PASSED
tests/test_auth.py::test_register_invalid_email PASSED
tests/test_auth.py::test_register_duplicate_email PASSED
tests/test_auth.py::test_register_weak_password PASSED
tests/test_auth.py::test_login_user PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_payments.py::test_create_payment PASSED
tests/test_payments.py::test_payment_status PASSED
tests/test_payments.py::test_commission_calculation PASSED
... (27 total)

======================== 27 passed in 2.34s ========================
```

---

### Ejecutar solo tests de autenticación
```bash
docker-compose exec -T app pytest tests/test_auth.py -v
```

---

### Ejecutar solo tests de pagos
```bash
docker-compose exec -T app pytest tests/test_payments.py -v
```

---

## INFORMACIÓN DEL SISTEMA

### Ver logs en vivo
```bash
docker-compose logs -f app
```

---

### Ver estado de contenedores
```bash
docker-compose ps
```

---

### Ver estadísticas de la BD
```bash
docker-compose exec db psql -U user -d taller_final -c "SELECT count(*) as total_users FROM users; SELECT count(*) as total_payments FROM payments;"
```

---

## SWAGGER UI (Alternativa a Curl)

Abre en el navegador: **http://localhost:8000/docs**

Desde ahí puedes:
- ✅ Ver todos los endpoints
- ✅ Ver esquemas (request/response)
- ✅ Ejecutar requests directamente
- ✅ Copiar curl equivalentes

---

## ⚡ QUICK COPY-PASTE FLOW

**Paso 1: Registra Usuario**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d '{"email":"juan@example.com","password":"Password123","full_name":"Juan Zuluaga"}'
```

**Paso 2: Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"juan@example.com","password":"Password123"}'
```

**Paso 3: Copia el token de la respuesta anterior y úsalo aquí:**
```bash
curl -X GET http://localhost:8000/api/v1/admin/metrics -H "Authorization: Bearer <PASTE-TOKEN-HERE>"
```

**Paso 4: Crear Pago**
```bash
curl -X POST http://localhost:8000/api/v1/payments/ -H "Authorization: Bearer <PASTE-TOKEN-HERE>" -H "Content-Type: application/json" -d '{"merchant_id":"MERCHANT_001","amount":100.00,"currency":"USD","method":"card"}'
```

---

**¡Que suerte en la sustentación! 🚀**

