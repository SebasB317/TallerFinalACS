# 🎬 CORRER TODO PASO A PASO

## ⚡ OPCIÓN 1: CON DOCKER (Recomendado)

### PASO 1: Instalar Docker

**Windows:**
1. Descargar: https://www.docker.com/products/docker-desktop
2. Instalar: Ejecutar el .exe
3. Reiniciar computadora
4. Abrir PowerShell y verificar:
```bash
docker --version
docker-compose --version
```

**Mac:**
```bash
brew install docker-desktop
```

**Linux:**
```bash
sudo apt install docker.io docker-compose
```

### PASO 2: Ir a la carpeta del proyecto

```bash
cd "c:\Users\JUAN ZULUAGA\Desktop\ACS\Taller Final"
```

Verificar que estás en la carpeta correcta:
```bash
dir  # Debe ver: docker-compose.yml, Dockerfile, app/, tests/
```

### PASO 3: Iniciar servicios con Docker Compose

```bash
docker-compose up -d
```

Esto:
- Descarga imagen de PostgreSQL
- Descarga imagen de Python
- Crea base de datos
- Inicia la aplicación
- ¡TODO automático!

### PASO 4: Verificar que todo está corriendo

```bash
docker-compose ps

# Debe verse algo como:
# NAME                    STATUS      PORTS
# taller_final_db         Up 2 min    5432/tcp
# taller_final_app        Up 1 min    0.0.0.0:8000->8000/tcp
```

### PASO 5: Ver logs (si algo falla)

```bash
docker-compose logs app

# Si ves errores, busca la línea roja
# Si ves "Uvicorn running on http://0.0.0.0:8000" ✓ OK
```

---

## ✅ EJERCICIO 1: AUTENTICACIÓN JWT

### PASO 1.1: Registrar Usuario

**Opción A: Con curl (terminal)**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"user@example.com\",
    \"password\": \"MyPassword123\",
    \"full_name\": \"Test User\"
  }"
```

**Respuesta esperada:**
```json
{
  "id": "a1b2c3d4-e5f6-47a1-8b9c-0d1e2f3a4b5c",
  "email": "user@example.com",
  "full_name": "Test User",
  "is_active": true
}
```

**Opción B: Con Swagger UI (más fácil)**
1. Abre: http://localhost:8000/docs
2. Busca: POST /api/v1/auth/register
3. Click en "Try it out"
4. Completa:
```json
{
  "email": "user@example.com",
  "password": "MyPassword123",
  "full_name": "Test User"
}
```
5. Click en "Execute"
6. Ver respuesta

### PASO 1.2: Hacer Login (Obtener Token)

**Opción A: Con curl**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"user@example.com\",
    \"password\": \"MyPassword123\"
  }"
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNCIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsImV4cCI6MTYzNDU2Nzg5MCwiaWF0IjoxNjM0NDgxNDkwfQ.xxx",
  "token_type": "bearer",
  "user_id": "a1b2c3d4-e5f6-47a1-8b9c-0d1e2f3a4b5c",
  "email": "user@example.com"
}
```

**⚠️ COPIA EL TOKEN (lo necesitarás para el Ejercicio 7)**

**Opción B: Swagger UI**
1. POST /api/v1/auth/login
2. Try it out
3. Ingresa credenciales
4. Execute
5. Copia el `access_token`

### PASO 1.3: Verificar Que Funciona

**Hacer que falle (para confirmar validaciones):**

```bash
# Email inválido
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"invalid-email\",
    \"password\": \"MyPassword123\"
  }"
# Respuesta: 422 (error de validación)

# Password muy corto
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"test@example.com\",
    \"password\": \"short\"
  }"
# Respuesta: 422 (error de validación)

# Password sin número
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"test@example.com\",
    \"password\": \"NoNumbers\"
  }"
# Respuesta: 422 (error de validación)
```

✅ **Ejercicio 1 completado** cuando:
- Registras usuario exitosamente
- Haces login exitosamente
- Obtienes token JWT
- Las validaciones funcionan

---

## ✅ EJERCICIO 7: MÉTRICAS

### PASO 7.1: Registrar Admin

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"admin@taller.local\",
    \"password\": \"AdminPass123\",
    \"full_name\": \"Administrator\"
  }"
```

### PASO 7.2: Login Admin (Obtener Token Admin)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"admin@taller.local\",
    \"password\": \"AdminPass123\"
  }"
```

**Copia el token admin en una variable (PowerShell):**

```powershell
$TOKEN_ADMIN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### PASO 7.3: Ver Métricas (Sin eventos aún)

```bash
# Reemplaza $TOKEN_ADMIN por tu token
curl -X GET http://localhost:8000/api/v1/admin/metrics \
  -H "Authorization: Bearer $TOKEN_ADMIN"
```

**Respuesta esperada (métricas iniciales):**
```json
{
  "timestamp": "2024-01-15T20:30:00",
  "uptime_seconds": 125.5,
  "payments": {
    "processed": 0,
    "failed": 0,
    "total": 0,
    "success_rate_percent": 0.0,
    "total_amount_usd": 0.0,
    "last_payment_time": null,
    "avg_payment_interval_seconds": null
  },
  "users": {
    "registered": 2,    ← 2 usuarios registrados
    "logins": 2         ← 2 logins realizados
  },
  "system": {
    "thread_count": 8
  }
}
```

✅ **Ejercicio 7 funciona** cuando:
- Ves el endpoint protegido (solo admin)
- Ves métricas de usuarios registrados
- Los números aumentan cuando registras más usuarios

---

## ✅ EJERCICIO 9: PAGOS INTERNACIONALES

### PASO 9.1: Registrar Merchant

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"merchant@test.com\",
    \"password\": \"MerchantPass123\"
  }"
```

### PASO 9.2: Login Merchant

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"merchant@test.com\",
    \"password\": \"MerchantPass123\"
  }"
```

**Guardar token en variable (PowerShell):**

```powershell
$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### PASO 9.3: Crear Pago #1 (USD - Card)

```bash
curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"merchant_id\": \"MERCHANT_001\",
    \"amount\": 100.00,
    \"currency\": \"USD\",
    \"method\": \"card\"
  }"
```

**Respuesta esperada:**
```json
{
  "id": "payment-uuid-1",
  "merchant_id": "MERCHANT_001",
  "amount": 100.00,
  "currency": "USD",
  "method": "card",
  "status": "pending",
  "commission": 0.00,
  "created_at": "2024-01-15T20:35:00",
  "updated_at": "2024-01-15T20:35:00"
}
```

**Guardar el ID:**
```powershell
$PAYMENT_ID_1 = "payment-uuid-1"
```

### PASO 9.4: Esperar 2 segundos (Worker procesa)

```bash
# Los workers están procesando en background
# Esperar a que termine
Start-Sleep -Seconds 2
```

### PASO 9.5: Ver Estado del Pago #1

```bash
curl -X GET http://localhost:8000/api/v1/payments/$PAYMENT_ID_1 \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (después de procesado):**
```json
{
  "payment_id": "payment-uuid-1",
  "status": "completed",          ← ¡COMPLETED!
  "amount": 100.00,
  "currency": "USD",
  "commission": 5.00,              ← 5% de comisión
  "net_amount": 95.00
}
```

### PASO 9.6: Crear Pago #2 (EUR - Card)

```bash
curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"merchant_id\": \"MERCHANT_002\",
    \"amount\": 150.50,
    \"currency\": \"EUR\",
    \"method\": \"card\"
  }"
```

**Guardar el ID:**
```powershell
$PAYMENT_ID_2 = "payment-uuid-2"
```

### PASO 9.7: Esperar y Ver Estado

```bash
Start-Sleep -Seconds 2

curl -X GET http://localhost:8000/api/v1/payments/$PAYMENT_ID_2 \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "payment_id": "payment-uuid-2",
  "status": "completed",
  "amount": 150.50,
  "currency": "EUR",
  "commission": 7.53,              ← 5% de €150.50
  "net_amount": 142.97
}
```

### PASO 9.8: Crear Pago #3 (GBP - Bank Transfer 2%)

```bash
curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"merchant_id\": \"MERCHANT_003\",
    \"amount\": 200.00,
    \"currency\": \"GBP\",
    \"method\": \"bank_transfer\"
  }"
```

**Guardar el ID:**
```powershell
$PAYMENT_ID_3 = "payment-uuid-3"
```

### PASO 9.9: Esperar y Ver Estado

```bash
Start-Sleep -Seconds 2

curl -X GET http://localhost:8000/api/v1/payments/$PAYMENT_ID_3 \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "payment_id": "payment-uuid-3",
  "status": "completed",
  "amount": 200.00,
  "currency": "GBP",
  "commission": 4.00,              ← 2% de £200
  "net_amount": 196.00
}
```

### PASO 9.10: Crear Pago #4 (JPY - Wallet 1%)

```bash
curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"merchant_id\": \"MERCHANT_004\",
    \"amount\": 10000.00,
    \"currency\": \"JPY\",
    \"method\": \"wallet\"
  }"
```

**Guardar el ID:**
```powershell
$PAYMENT_ID_4 = "payment-uuid-4"
```

### PASO 9.11: Esperar y Ver Estado

```bash
Start-Sleep -Seconds 2

curl -X GET http://localhost:8000/api/v1/payments/$PAYMENT_ID_4 \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "payment_id": "payment-uuid-4",
  "status": "completed",
  "amount": 10000.00,
  "currency": "JPY",
  "commission": 100.00,            ← 1% de ¥10000
  "net_amount": 9900.00
}
```

✅ **Ejercicio 9 funciona** cuando:
- Creas pagos exitosamente
- Los workers los procesan (status: completed)
- Las comisiones se calculan correctamente
- Las conversiones de moneda funcionan

---

## 📊 VER MÉTRICAS ACTUALIZADAS

### Después de Ejercicio 9

Vuelve a ver las métricas:

```bash
curl -X GET http://localhost:8000/api/v1/admin/metrics \
  -H "Authorization: Bearer $TOKEN_ADMIN"
```

**Respuesta esperada:**
```json
{
  "timestamp": "2024-01-15T20:40:00",
  "uptime_seconds": 245.5,
  "payments": {
    "processed": 4,                  ← 4 pagos procesados
    "failed": 0,
    "total": 4,
    "success_rate_percent": 100.0,   ← 100% éxito
    "total_amount_usd": 765.50,      ← Suma en USD
    "last_payment_time": "2024-01-15T20:39:55",
    "avg_payment_interval_seconds": 2.5
  },
  "users": {
    "registered": 5,                 ← 5 usuarios (3 + admin + merchant)
    "logins": 5
  },
  "system": {
    "thread_count": 12
  }
}
```

---

## 🧪 EJECUTAR TESTS

### Todos los tests

```bash
docker-compose exec app pytest tests/ -v
```

**Verás:**
```
tests/test_email.py PASSED
tests/test_password.py PASSED
tests/test_bcrypt.py PASSED
tests/test_auth_service.py PASSED
tests/test_payment_service.py PASSED
tests/test_metrics.py PASSED

========== 6 passed in 1.23s ==========
```

### Test específico

```bash
# Solo Ejercicio 1
docker-compose exec app pytest tests/test_auth_service.py -v

# Solo Ejercicio 7
docker-compose exec app pytest tests/test_metrics.py -v

# Solo Ejercicio 9
docker-compose exec app pytest tests/test_payment_service.py -v
```

---

## 🎮 DEMO AUTOMÁTICA (Ejercicio 9)

**Ver demo interactiva con productores y workers:**

```bash
docker-compose exec app python demo_payment_exercise9.py
```

**Verás en tiempo real:**
```
[Worker-1] Iniciado y esperando pagos...
[Worker-2] Iniciado y esperando pagos...
[Worker-3] Iniciado y esperando pagos...

[Productor 1] Iniciado
[Productor 1] Encolando pago: MERCHANT_101 | 50.00 EUR

[Worker 1] Procesando pago: payment-uuid-123
...
[Worker 1] ✓ Pago completado: payment-uuid-123
  Monto: 50.00 EUR
  Comisión: 2.50 USD
  Neto: 47.50 USD
```

---

## ✅ CHECKLIST COMPLETO

### Ejercicio 1: Autenticación
- [ ] Registrar usuario
- [ ] Login exitoso
- [ ] Obtener token JWT
- [ ] Validaciones funcionan
- [ ] Tests pasan

### Ejercicio 7: Métricas
- [ ] Acceder a /admin/metrics
- [ ] Ver usuarios registrados
- [ ] Ver logins
- [ ] Solo admin puede acceder

### Ejercicio 9: Pagos
- [ ] Crear pago en USD
- [ ] Crear pago en EUR
- [ ] Crear pago en GBP
- [ ] Crear pago en JPY
- [ ] Workers procesan (status = completed)
- [ ] Comisiones correctas (5%, 2%, 1%)
- [ ] Métricas actualizadas

### General
- [ ] Docker corriendo
- [ ] API en http://localhost:8000
- [ ] Swagger en http://localhost:8000/docs
- [ ] Tests pasando
- [ ] Demo ejecutándose

---

## 🛑 DETENER TODO

```bash
docker-compose down
```

**Para limpiar TODO (incluyendo BD):**
```bash
docker-compose down -v
```

---

## 🐛 TROUBLESHOOTING

### Puerto 8000 ocupado
```bash
netstat -ano | findstr :8000
# Encontrar PID y matar:
taskkill /PID <PID> /F
```

### BD no se conecta
```bash
docker-compose logs postgres
# Debe decir: "database system is ready to accept connections"
```

### App no inicia
```bash
docker-compose logs app
# Buscar líneas rojas de error
```

### Necesito resetear BD
```bash
docker-compose down -v
docker-compose up -d
```

---

## 📍 RESUMEN

| Paso | Ejercicio | Comando | Esperado |
|------|-----------|---------|----------|
| 1 | General | `docker-compose up -d` | Servicios corriendo |
| 2 | Ej 1 | `POST /auth/register` | Usuario creado |
| 3 | Ej 1 | `POST /auth/login` | Token JWT |
| 4 | Ej 7 | `GET /admin/metrics` | Métricas visibles |
| 5 | Ej 9 | `POST /payments/` | Pago creado |
| 6 | Ej 9 | `GET /payments/{id}` | Status: completed |
| 7 | General | `pytest tests/` | Todos pasan |
| 8 | General | `python demo_payment_exercise9.py` | Demo corre |

---

**¡Listo! Sigue los pasos y tendrás todo funcionando. ¡Buena suerte! 🚀**
