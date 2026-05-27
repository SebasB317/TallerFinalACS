# 🎓 MANUAL DE SUSTENTACIÓN - TALLER FINAL
## Arquitectura Limpia + Pagos Internacionales + Concurrencia

**Fecha de sustentación:** Jueves (Semana del 26 de Mayo, 2026)  
**Duración estimada:** 30-45 minutos  
**Requisitos:** Docker corriendo, Postman o curl

---

## 📋 ÍNDICE DE PRUEBAS

1. **EJERCICIO 1: Autenticación JWT** (10 min)
2. **EJERCICIO 7: Dashboard Administrativo** (10 min)
3. **EJERCICIO 9: Pagos Internacionales** (15 min)
4. **Tests Unitarios** (5 min)

---

## ✅ EJERCICIO 1: AUTENTICACIÓN JWT

### Objetivo
Demostrar un sistema de autenticación seguro con JWT.

### Prueba 1.1: Registrar Usuario

**Paso 1:** Abre Postman o curl

**Paso 2:** Haz esta solicitud:
```
POST http://localhost:8000/api/v1/auth/register
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "Password123",
  "full_name": "Juan Zuluaga"
}
```

**Respuesta esperada (201 Created):**
```json
{
  "id": "uuid-aqui",
  "email": "juan@example.com",
  "full_name": "Juan Zuluaga",
  "is_active": true
}
```

**Qué demuestra:**
- ✅ Validación de email
- ✅ Validación de contraseña (min 8 caracteres, mayúscula, número)
- ✅ Hash de contraseña con bcrypt
- ✅ Almacenamiento en BD

---

### Prueba 1.2: Validaciones Funcionan

**FALLO 1: Email inválido**
```
POST http://localhost:8000/api/v1/auth/register

{
  "email": "invalid-email",
  "password": "Password123"
}
```
**Respuesta:** 422 (Unprocessable Entity) - "value is not a valid email address"  
**Demuestra:** ✅ Validación de email funciona

**FALLO 2: Contraseña sin número**
```
{
  "email": "test@example.com",
  "password": "NoNumeros"
}
```
**Respuesta:** 422 - "Password must contain at least one number"  
**Demuestra:** ✅ Validación de contraseña funciona

**FALLO 3: Email duplicado**
```
{
  "email": "juan@example.com",  # Ya registrado
  "password": "Password123"
}
```
**Respuesta:** 409 - "Usuario con email ... ya existe"  
**Demuestra:** ✅ Prevención de duplicados

---

### Prueba 1.3: Login y Obtener Token JWT

**Paso 1:** Haz login
```
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "Password123"
}
```

**Respuesta esperada (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "uuid-aqui",
  "email": "juan@example.com"
}
```

**Qué demuestra:**
- ✅ Verificación de contraseña (bcrypt)
- ✅ Generación de JWT token
- ✅ Token con información del usuario

**Paso 2:** COPIA el token (sin las comillas)

---

### Prueba 1.4: Usar el Token (Autorización)

**Paso 1:** Intenta acceder sin token
```
GET http://localhost:8000/api/v1/admin/metrics
```
**Respuesta:** 401 - "No autorizado"  
**Demuestra:** ✅ Endpoint protegido

**Paso 2:** Intenta acceder CON token
```
GET http://localhost:8000/api/v1/admin/metrics
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**Respuesta:** 200 - Retorna métricas  
**Demuestra:** ✅ Token válido = Acceso permitido

---

## ✅ EJERCICIO 7: DASHBOARD ADMINISTRATIVO

### Objetivo
Demostrar un endpoint de monitoreo del sistema con acceso protegido por rol.

### Prueba 7.1: Registrar Usuario Admin

```
POST http://localhost:8000/api/v1/auth/register

{
  "email": "admin@example.com",
  "password": "AdminPass123",
  "full_name": "Administrador"
}
```

**Respuesta:** 201 Created

---

### Prueba 7.2: Login como Admin

```
POST http://localhost:8000/api/v1/auth/login

{
  "email": "admin@example.com",
  "password": "AdminPass123"
}
```

**Copia el token de la respuesta**

---

### Prueba 7.3: Acceder a Métricas (Sin autenticación)

```
GET http://localhost:8000/api/v1/admin/metrics
```

**Respuesta:** 401 - "No autorizado"  
**Demuestra:** ✅ Autenticación requerida

---

### Prueba 7.4: Acceder a Métricas (Con token admin)

```
GET http://localhost:8000/api/v1/admin/metrics
Authorization: Bearer <admin-token>
```

**Respuesta esperada (200):**
```json
{
  "timestamp": "2026-05-27T03:30:00",
  "uptime_seconds": 125.5,
  "payments": {
    "processed": 15,
    "failed": 0,
    "total": 15,
    "success_rate_percent": 100.0,
    "total_amount_usd": 2500.00,
    "last_payment_time": "2026-05-27T03:29:50",
    "avg_payment_interval_seconds": 0.85
  },
  "users": {
    "registered": 2,
    "logins": 2
  },
  "system": {
    "thread_count": 8
  }
}
```

**Qué demuestra:**
- ✅ Endpoint protegido (requiere autenticación)
- ✅ Métricas en tiempo real
- ✅ Estadísticas de pagos y usuarios
- ✅ Información del sistema (threads activos)
- ✅ Patrón Singleton (una única instancia)
- ✅ Thread-safe (RLock)

---

### Prueba 7.5: Usuario normal NO puede acceder

**Registra otro usuario NO-admin:**
```
POST http://localhost:8000/api/v1/auth/register

{
  "email": "user@example.com",
  "password": "UserPass123",
  "full_name": "Usuario Normal"
}
```

**Intenta acceder a métricas con ese usuario:**
```
GET http://localhost:8000/api/v1/admin/metrics
Authorization: Bearer <user-token>
```

**Respuesta:** 403 - "Solo administradores pueden acceder"  
**Demuestra:** ✅ Control de acceso por rol (RBAC)

---

## ✅ EJERCICIO 9: PAGOS INTERNACIONALES

### Objetivo
Demostrar procesamiento concurrente de pagos con sincronización multihilo.

### PARTE 1: Cola de Pagos con Workers

### Prueba 9.1: Crear Pago

**Usuario:** juan@example.com (debe estar logueado)

```
POST http://localhost:8000/api/v1/payments/
Authorization: Bearer <juan-token>
Content-Type: application/json

{
  "merchant_id": "MERCHANT_001",
  "amount": 100.00,
  "currency": "USD",
  "method": "card"
}
```

**Respuesta esperada (201):**
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

**Qué demuestra:**
- ✅ Creación de pago
- ✅ Estado: PENDING (en cola de procesamiento)
- ✅ Almacenamiento en BD

**COPIA el payment_id para la siguiente prueba**

---

### Prueba 9.2: Esperar a que se procese (Workers)

**Espera 3 segundos** (tiempo para que los workers procesen)

---

### Prueba 9.3: Obtener estado del pago (Procesado)

```
GET http://localhost:8000/api/v1/payments/<payment-id>
Authorization: Bearer <juan-token>
```

**Respuesta esperada (200):**
```json
{
  "payment_id": "payment-uuid-1",
  "status": "completed",
  "amount": 100.0,
  "currency": "USD",
  "commission": 5.0,
  "net_amount": 95.0
}
```

**Qué demuestra:**
- ✅ Estado cambió de PENDING a COMPLETED
- ✅ Comisión calculada (5% para card)
- ✅ Workers procesaron el pago
- ✅ Queue.Queue thread-safe funcionó

---

### PARTE 2: Read-Write Lock (Si tienes tiempo extra)

### Prueba 9.4: Crear múltiples pagos (diferentes monedas)

**Pago en EUR:**
```
POST http://localhost:8000/api/v1/payments/
Authorization: Bearer <juan-token>

{
  "merchant_id": "MERCHANT_002",
  "amount": 150.50,
  "currency": "EUR",
  "method": "card"
}
```

**Pago en GBP:**
```
{
  "merchant_id": "MERCHANT_003",
  "amount": 200.00,
  "currency": "GBP",
  "method": "bank_transfer"
}
```

**Qué demuestra:**
- ✅ Soporte de múltiples monedas
- ✅ Diferentes métodos de pago
- ✅ Conversión a USD (verificar en métricas)

---

## ✅ TESTS UNITARIOS

### Prueba 10.1: Ejecutar todos los tests

**En terminal:**
```bash
docker-compose exec -T app pytest tests/ -v
```

**Resultado esperado:**
```
✅ 27 tests passed
```

**Qué demuestra:**
- ✅ Validación de email
- ✅ Hash de contraseña (bcrypt)
- ✅ Validación de pago
- ✅ Cálculo de comisión
- ✅ Conversión de monedas
- ✅ Thread-safety de métricas

---

## 📊 GUIÓN DE SUSTENTACIÓN (MINUTO A MINUTO)

### Minutos 0-2: Introducción
```
"He implementado un sistema de Pagos Internacionales con 
Arquitectura Limpia que demuestra:
1. Autenticación segura (JWT + bcrypt)
2. Dashboard administrativo (Singleton + Métricas)
3. Procesamiento concurrente de pagos (Workers + Threading)
"
```

### Minutos 2-12: Demostración EJERCICIO 1
```
1. Mostrar POST /auth/register
2. Mostrar validaciones fallando
3. Mostrar POST /auth/login
4. Mostrar JWT token generado
```

### Minutos 12-22: Demostración EJERCICIO 7
```
1. Registrar admin
2. Mostrar acceso sin token (401)
3. Mostrar acceso como usuario normal (403)
4. Mostrar acceso como admin (200)
5. Explicar métricas thread-safe
```

### Minutos 22-37: Demostración EJERCICIO 9
```
1. Crear pago (status: pending)
2. Esperar 3 segundos (workers procesando)
3. Obtener pago procesado (status: completed)
4. Mostrar comisión calculada
5. Crear pagos en EUR, GBP
6. Explicar Queue, Workers, Threading
```

### Minutos 37-42: Tests
```
1. Ejecutar pytest
2. Mostrar 27/27 pasando
3. Mencionar cobertura de todas las funcionalidades
```

### Minutos 42-45: Conclusión
```
"El sistema demuestra:
- ✅ Arquitectura Limpia (Domain, Application, Infrastructure, Presentation)
- ✅ Domain-Driven Design
- ✅ Patrones de Diseño (Singleton, Repository, Factory, etc)
- ✅ Seguridad (JWT, Bcrypt, RBAC)
- ✅ Concurrencia (Thread-safe, RLock, Queue, Barrier)
- ✅ Tests (27 unitarios + integración)
"
```

---

## 🎯 RESPUESTAS A PREGUNTAS COMUNES

### P: ¿Qué es Arquitectura Limpia?
**R:** Separación clara entre capas (Domain, Application, Infrastructure, Presentation) permitiendo cambiar tecnologías sin afectar la lógica de negocio.

### P: ¿Por qué JWT y no sesiones?
**R:** JWT es stateless, escalable, y permite autenticación distribuida entre microservicios.

### P: ¿Cómo garantizas thread-safety?
**R:** Uso de threading.RLock en MetricsCollector, queue.Queue para productor-consumidor, y operaciones atómicas.

### P: ¿Qué es el Patrón Singleton?
**R:** Una única instancia de MetricsCollector compartida en toda la aplicación.

### P: ¿Cómo funciona el procesamiento de pagos?
**R:** Los pagos se encolan en queue.Queue, 3 workers Thread consumen de la cola, procesan (validación, comisión, conversión) y actualizan estado en BD.

---

## 🚀 CHECKLIST ANTES DE SUSTENTAR

```
[ ] Docker corriendo: docker-compose ps
[ ] Prueba registro: POST /auth/register
[ ] Prueba login: POST /auth/login (copiar token)
[ ] Prueba métricas: GET /admin/metrics
[ ] Prueba pago: POST /payments/
[ ] Tests pasando: pytest tests/ -v
[ ] Swagger UI disponible: http://localhost:8000/docs
[ ] Base de datos respondiendo
[ ] Laptop cargada 100%
```

---

## 📱 ACCESOS RÁPIDOS

**API Docs:** http://localhost:8000/docs
**Health Check:** http://localhost:8000/
**Logs en vivo:** `docker-compose logs -f app`
**Ver estado:** `docker-compose ps`

---

## 💡 TIPS PARA LA SUSTENTACIÓN

1. **Practica el flujo** antes del jueves
2. **Ten los tokens copiados** en notepad
3. **Explica qué demuestra cada prueba**
4. **Muestra el código** si preguntan por detalles
5. **Menciona los patrones** aplicados
6. **Habla de seguridad** (JWT, bcrypt, RBAC)
7. **Explica la concurrencia** (threads, locks, queue)

---

**¡Éxito en tu sustentación! 🎓**

Estás mostrando un proyecto profesional con arquitectura real de producción.

