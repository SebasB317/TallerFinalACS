# ✅ CHECKLIST PRESENTACIÓN JUEVES

## PRE-PRESENTACIÓN (30 minutos antes)

```
[ ] Laptop cargada 100%
[ ] WiFi funcionando
[ ] Docker Desktop abierto
[ ] Terminal lista (PowerShell)
[ ] Postman abierto (o curl listo)
[ ] Este documento abierto en navegador
[ ] Respirar profundo 😌
```

---

## VERIFICACIONES TÉCNICAS (15 minutos antes)

### 1. Iniciar Docker
```bash
cd "C:\Users\JUAN ZULUAGA\Desktop\ACS\Taller Final"
docker-compose up -d
```

```
[ ] Docker containers levantados
[ ] PostgreSQL corriendo ✅
[ ] FastAPI corriendo ✅
```

### 2. Verificar estado
```bash
docker-compose ps
```

**Esperado:**
```
NAME           STATUS
db             Up (healthy)
app            Up
```

```
[ ] Ambos servicios "UP"
```

### 3. Probar conectividad
```bash
curl http://localhost:8000/docs
```

**Esperado:**
```
200 OK
```

```
[ ] API responde
[ ] Swagger UI disponible
```

---

## DURANTE LA PRESENTACIÓN

### ESCENA 1: Introducción (2 minutos)

**Qué decir:**
```
"Buenos días/tardes.

Soy Juan Zuluaga y voy a presentar el Taller Final.

Mi proyecto es un Sistema de Pagos Internacionales que 
demuestra:

✅ Arquitectura Limpia
✅ Autenticación segura (JWT)
✅ Procesamiento concurrente
✅ Patrones de diseño reales

Todo está dockerizado, testeado, y documentado.

Empecemos."
```

```
[ ] Hiciste contacto visual
[ ] Hablaste claro y seguro
```

---

### ESCENA 2: EJERCICIO 1 - Autenticación (10 minutos)

**Paso 1: Mostrar archivo de documentación**
```
Abre: MANUAL_SUSTENTACION.md
Lee: "EJERCICIO 1: AUTENTICACIÓN JWT"
```

```
[ ] Documentación visible en pantalla
```

**Paso 2: Abrir Postman**
```
Collection → New Request
Method: POST
URL: http://localhost:8000/api/v1/auth/register
Body (JSON):
{
  "email": "demo@example.com",
  "password": "DemoPass123",
  "full_name": "Demo User"
}
```

```
[ ] Request configurado
[ ] Presionaste SEND
[ ] Respuesta 201 OK
[ ] Usuario creado
```

**Paso 3: Explicar qué pasó**
```
"Aquí creamos un usuario con:
- Email válido (validación con email-validator)
- Contraseña fuerte (8+ caracteres, números, mayúsculas)
- Bcrypt para hashear la contraseña (irreversible)
"
```

```
[ ] Explicación clara
```

**Paso 4: Mostrar FALLO - Email inválido**
```
Cambiar JSON:
{
  "email": "invalid-email",
  "password": "DemoPass123"
}
SEND
```

**Esperado:** 422 Unprocessable Entity

```
[ ] Error mostrado correctamente
[ ] Explicaste por qué falló
```

**Paso 5: Login y obtener Token**
```
POST http://localhost:8000/api/v1/auth/login
Body:
{
  "email": "demo@example.com",
  "password": "DemoPass123"
}
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

```
[ ] Token generado
[ ] Copiaste el token
```

**Paso 6: Usar Token**
```
GET http://localhost:8000/api/v1/admin/metrics
Headers:
Authorization: Bearer <token-copiado>
```

```
[ ] Respuesta 200
[ ] Endpoint protegido funcionando
[ ] Explicaste cómo funciona JWT
```

---

### ESCENA 3: EJERCICIO 7 - Dashboard Admin (10 minutos)

**Paso 1: Explicar RBAC**
```
"Role-Based Access Control significa que diferentes 
usuarios tienen diferentes permisos:

- Usuario normal: Puede crear pagos, ver sus pagos
- Admin: Puede ver métricas de TODO el sistema
"
```

```
[ ] Concepto claro
```

**Paso 2: Intentar acceso sin token**
```
GET http://localhost:8000/api/v1/admin/metrics
(SIN Authorization header)
```

**Esperado:** 401 Unauthorized

```
[ ] Error 401 mostrado
[ ] Explicaste por qué se necesita token
```

**Paso 3: Registrar otro usuario**
```
POST http://localhost:8000/api/v1/auth/register
{
  "email": "usuario@example.com",
  "password": "UserPass123",
  "full_name": "Usuario Normal"
}
```

```
[ ] Usuario creado
```

**Paso 4: Login como usuario normal**
```
POST http://localhost:8000/api/v1/auth/login
{
  "email": "usuario@example.com",
  "password": "UserPass123"
}
```

```
[ ] Token obtenido
```

**Paso 5: Intentar acceder métricas como usuario normal**
```
GET http://localhost:8000/api/v1/admin/metrics
Authorization: Bearer <user-token>
```

**Esperado:** 403 Forbidden

```
[ ] Error 403 mostrado
[ ] Explicaste RBAC
```

**Paso 6: Acceder como admin (token del primer usuario)**
```
GET http://localhost:8000/api/v1/admin/metrics
Authorization: Bearer <admin-token>
```

**Esperado:** 200 OK con métricas

```json
{
  "timestamp": "...",
  "payments": {
    "processed": X,
    "success_rate_percent": 100.0,
    "total_amount_usd": Y
  },
  "users": {
    "registered": 2
  }
}
```

```
[ ] Métricas visibles
[ ] Explicaste qué cada métrica significa
[ ] Mencionaste Singleton + RLock (thread-safe)
```

---

### ESCENA 4: EJERCICIO 9 - Pagos Internacionales (15 minutos)

**Parte A: Crear Pago USD**

**Paso 1: Crear pago**
```
POST http://localhost:8000/api/v1/payments/
Authorization: Bearer <admin-token>
{
  "merchant_id": "MERCHANT_001",
  "amount": 100.00,
  "currency": "USD",
  "method": "card"
}
```

**Respuesta:**
```json
{
  "id": "payment-uuid-1",
  "status": "pending",
  "amount": 100.0,
  "currency": "USD",
  "commission": 0
}
```

```
[ ] Pago creado
[ ] Status es "pending"
[ ] Comisión aún 0 (se calcula al procesar)
[ ] COPIA el payment-id
```

**Paso 2: Explicar flujo**
```
"El pago se envía a una COLA (Queue).
Hay 3 WORKERS (threads) procesando.
Cada worker:
1. Obtiene pago de la cola
2. Calcula comisión (5% para card)
3. Convierte a USD (si es otra moneda)
4. Actualiza estado a 'completed'
5. Guarda en BD

Todo esto es thread-safe usando:
- Queue (producer-consumer)
- RLock (mutex para acceso compartido)
- ReadWriteLock (múltiples lectores, escritor exclusivo)
"
```

```
[ ] Explicación clara
[ ] Mencionaste threading
```

**Paso 3: Esperar**
```
(Espera 3 segundos - los workers procesan)

Tiempo: ⏱️ 3 segundos
```

```
[ ] Esperaste pacientemente
```

**Paso 4: Verificar pago procesado**
```
GET http://localhost:8000/api/v1/payments/payment-uuid-1
Authorization: Bearer <admin-token>
```

**Respuesta:**
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

```
[ ] Status cambió a "completed"
[ ] Comisión se calculó (5%)
[ ] Net_amount = 100 - 5 = 95
[ ] Explicaste el cálculo
```

**Parte B: Pagos en Otras Monedas**

**Paso 5: Crear pago en EUR**
```
POST http://localhost:8000/api/v1/payments/
Authorization: Bearer <admin-token>
{
  "merchant_id": "MERCHANT_002",
  "amount": 150.50,
  "currency": "EUR",
  "method": "card"
}
```

```
[ ] Pago EUR creado
```

**Paso 6: Crear pago en GBP con bank_transfer**
```
POST http://localhost:8000/api/v1/payments/
Authorization: Bearer <admin-token>
{
  "merchant_id": "MERCHANT_003",
  "amount": 200.00,
  "currency": "GBP",
  "method": "bank_transfer"
}
```

```
[ ] Pago GBP creado
[ ] Explicaste diferentes métodos de pago
```

**Paso 7: Esperar y verificar**
```
(Espera 3 segundos)

GET http://localhost:8000/api/v1/payments/
Authorization: Bearer <admin-token>
```

**Esperado:**
```json
{
  "payments": [
    {"id": "uuid-1", "currency": "USD", "status": "completed"},
    {"id": "uuid-2", "currency": "EUR", "status": "completed"},
    {"id": "uuid-3", "currency": "GBP", "status": "completed"}
  ]
}
```

```
[ ] 3 pagos completados
[ ] Diferentes monedas procesadas
[ ] Conversión a USD funcionó
```

**Paso 8: Explicar concurrencia**

```
"Todo esto demuestra concurrencia real:

1. PRODUCTOR (API): Envía pagos a la cola
2. CONSUMIDOR (Workers): 3 threads procesan
   - Los 3 pueden leer/escribir simultáneamente
   - Sin corrupción de datos (RLock)
   
3. BARRIER: Sincroniza conversión de monedas
   - Los 3 threads esperan en un punto
   - Luego consolidan el total

4. READWRITELOCK: Múltiples lectores de tasas
   - 100 threads pueden leer tasas simultáneamente
   - Solo 1 thread puede escribir tasas (exclusivo)
"
```

```
[ ] Explicación técnica clara
[ ] Mencionaste threading
[ ] Mencionaste sincronización
```

---

### ESCENA 5: Tests (5 minutos)

**Paso 1: Ejecutar tests**
```bash
docker-compose exec -T app pytest tests/ -v
```

**Esperado:**
```
tests/test_auth.py::test_register_user PASSED
tests/test_auth.py::test_invalid_email PASSED
... 25 more tests ...

======================== 27 passed in 2.34s ========================
```

```
[ ] Todos los tests pasan
[ ] 27/27 ✅
```

**Paso 2: Explicar cobertura**

```
"Los 27 tests cubren:

✅ Autenticación:
   - Registro con validación
   - Email duplicado
   - Contraseña débil
   - Login exitoso
   - Login fallido

✅ Pagos:
   - Creación
   - Estado pending → completed
   - Cálculo de comisión
   - Conversión de monedas

✅ Métricas:
   - Acceso autenticado
   - Acceso no autenticado
   - Acceso como admin
   - Acceso como usuario normal
"
```

```
[ ] Tests explicados
```

---

### ESCENA 6: Conclusión (5 minutos)

**Resumen**

```
"Resumiendo lo que vimos:

ARQUITECTURA:
✅ Arquitectura Limpia (Domain, Application, Infrastructure, Presentation)
✅ Domain-Driven Design (Entidades, Value Objects, Servicios)
✅ Separación clara de responsabilidades

SEGURIDAD:
✅ Autenticación JWT (stateless, escalable)
✅ Contraseñas con bcrypt (hashing seguro)
✅ Role-Based Access Control (RBAC)
✅ Headers de autenticación protegidos

CONCURRENCIA:
✅ Threads para procesamiento paralelo
✅ Queue para productor-consumidor
✅ RLock para mutex (mutual exclusion)
✅ ReadWriteLock para optimizar lecturas
✅ Barrier para sincronización

PATRONES:
✅ Singleton (MetricsCollector)
✅ Repository (Abstracción de BD)
✅ Dependency Injection (FastAPI)
✅ Strategy (Diferentes métodos de pago)
✅ Worker Pool (Procesamiento paralelo)

TESTING:
✅ 27 tests unitarios
✅ Integración manual

RESULTADOS:
✅ Sistema completamente funcional
✅ Dockerizado
✅ Escalable
✅ Mantenible
✅ Production-ready
"
```

```
[ ] Resumen memorable
```

**Agradecimiento**

```
"Gracias por la atención.

¿Preguntas?"
```

```
[ ] Sonreír
[ ] Esperar preguntas
```

---

## MANEJO DE PREGUNTAS

**Si preguntan:**

```
"¿Qué es Arquitectura Limpia?"
→ Ver: PREGUNTAS_TECNICAS.md → P1

"¿Por qué JWT?"
→ Ver: PREGUNTAS_TECNICAS.md → P5

"¿Cómo protegiste contraseñas?"
→ Ver: PREGUNTAS_TECNICAS.md → P4

"¿Qué es RLock?"
→ Ver: PREGUNTAS_TECNICAS.md → P8

... y así
```

```
[ ] Respondiste sin dudas
[ ] Si no sabes, dilo (honestidad)
[ ] Ofrécete a investigar después
```

---

## PROBLEMAS COMUNES Y SOLUCIONES

| Problema | Solución |
|----------|----------|
| Docker no inicia | `docker-compose down -v && docker-compose up -d` |
| API no responde | `docker-compose logs -f app` (ver errores) |
| Pago no se procesa | Esperar 3-5 segundos (workers procesando) |
| Token inválido | Copiar sin comillas, formato correcto |
| Error 403 en admin | Usuario no es admin (email no está en ADMIN_EMAILS) |
| Nervios | Respirar profundo, es solo demostración, sabes tu proyecto |

```
[ ] Problemas memorizados
```

---

## DESPUÉS DE LA PRESENTACIÓN

```
[ ] Agradeciste por el tiempo
[ ] Preguntaste "¿Algo más?"
[ ] Esperaste feedback
[ ] Cerrar Docker limpiamente (opcional)
[ ] Ir a celebrar 🎉
```

---

## NOTAS FINALES

**Confianza:**
- Practicaste esto
- Tu código está limpio
- Tests pasan
- Documentación completa
- Sabes tu proyecto mejor que nadie

**Actitud:**
- Habla con seguridad
- Explica con claridad
- Muestra con orgullo
- Escucha las preguntas completamente
- Responde honestamente

**Timing:**
- 2 min: Intro
- 10 min: JWT
- 10 min: Admin
- 15 min: Pagos
- 5 min: Tests
- 3 min: Conclusión
- 5 min: Preguntas

**Total: ~50 minutos**

---

**¡ESTÁS LISTO! 🚀**

Mucho éxito el jueves.

Tu proyecto es profesional, está bien documentado, y demostrará 
exactamente lo que se pidió.

**¡Vamos! 💪**

