# Taller Final — Documento general

## Objetivo

Implementar un sistema distribuido y concurrente para procesamiento de tareas en segundo plano, siguiendo **Clean Architecture**, con API REST (FastAPI), autenticación JWT, cola de trabajos, workers, WebSockets, métricas y ejercicios adicionales de concurrencia descritos en el enunciado.

## Estado del proyecto

| Historia | Descripción | Estado |
|----------|-------------|--------|
| #1 | Usuarios y autenticación (JWT) | **Completada** |
| #2 | Envío de tareas (productor-consumidor) | **Completada** |
| #3 | Workers y análisis de sentimiento | **Completada** |
| #4 | Consultas, resultados y reportes | **Completada** |
| #5 | Notificaciones (WebSocket / webhook) | Pendiente |
| #6 | Cancelación y prioridad | Pendiente |
| #7 | Dashboard `/admin/metrics` | Pendiente |
| #8 | LMS (colas, RW-lock, barrera) | Pendiente |
| #9 | Pagos internacionales | Pendiente |

## Estructura de carpetas

```
Taller Final/
├── DOCUMENTO_GENERAL.md    # Este archivo
├── requirements.txt
├── pytest.ini
├── app/
│   ├── main.py             # Punto de entrada FastAPI
│   ├── config.py           # Settings (env)
│   ├── domain/             # Entidades, VOs, contratos
│   ├── application/      # Casos de uso y servicios
│   ├── infrastructure/   # BD, cola, workers, seguridad
│   └── presentation/     # Routers, schemas, dependencias HTTP
└── tests/
```

## Entorno de Python

Se recomienda **Python 3.11 o 3.12** para máxima compatibilidad con todas las librerías. En **Python 3.14** las dependencias usan versiones recientes con ruedas precompiladas (`requirements.txt` sin versiones fijas estrictas).

## Cómo ejecutar

1. Crear entorno virtual (recomendado) e instalar dependencias (incluye `email-validator`, necesario para `EmailStr` en registro/login):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Variables de entorno opcionales (por defecto sirve para desarrollo):

   - `SECRET_KEY`: clave para firmar JWT (cambiar en producción).
   - `DATABASE_URL`: por defecto `sqlite:///./taller_final.db`.
   - `WORKER_COUNT`: hilos consumidores de la cola (por defecto `4`).
   - `MAX_TEXTS_PER_JOB`: tope del lote (por defecto `100`, alineado al enunciado).
   - `ANALYSIS_SLEEP_MIN_SEC` / `ANALYSIS_SLEEP_MAX_SEC`: rango del `sleep` simulado por texto (~50 ms por defecto).
   - `SIMULATED_ANALYSIS_TIMEOUT_PROBABILITY`: probabilidad de timeout simulado por texto (`0` por defecto; p.ej. `0.03` para demos).

3. Arrancar la API:

   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. Documentación interactiva: `http://127.0.0.1:8000/docs` (cambia el puerto si usas otro en el paso 3).

### Windows: `WinError 10013` al arrancar Uvicorn

Significa que **Windows no deja enlazar ese puerto** (reserva del sistema, otro programa, VPN, Hyper-V, rango excluido, etc.). Prueba **otro puerto**, por ejemplo **8080** u **8888**:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Luego abre `http://127.0.0.1:8080/docs`. Para ver qué usa el 8000: `netstat -ano | findstr :8000` en PowerShell.

5. Pruebas:

   ```bash
   pytest tests/ -v
   ```

## Reglas de negocio relevantes (Historia #1)

- El usuario se identifica por **email único**.
- La contraseña debe tener **al menos 8 caracteres**, **una mayúscula** y **un número**.
- El **JWT expira a las 24 horas**.
- La contraseña **nunca** se persiste en texto plano (hash con bcrypt).

## Endpoints (API)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/register` | Registro `{ "email", "password" }` → 201 + `user_id` |
| POST | `/login` | Login → `{ "access_token", "token_type" }` |
| GET | `/me` | Usuario actual (requiere `Authorization: Bearer ...`) |
| GET | `/analyze` | Ejemplo de endpoint protegido (requiere Bearer) |
| GET | `/health` | Comprobación pública de que el servicio responde |
| POST | `/jobs` | Crea trabajo `{ "texts": [...] }` → **202** `{ job_id, status: "pending" }` (requiere Bearer) |
| GET | `/jobs/{job_id}` | Estado y progreso: `status`, `total_texts`, `processed_texts` (requiere Bearer, solo el dueño) |
| GET | `/jobs/{job_id}/results` | Textos paginados: `page`, `per_page` (1–100) (requiere Bearer) |
| GET | `/jobs/{job_id}/report` | Conteos POSITIVE/NEGATIVE/NEUTRAL y `average_score` si `status == completed` (**400** si aún procesa) (requiere Bearer) |

## Reglas de negocio relevantes (Historia #2)

- Lote máximo **100** textos; si se supera → **400**.
- Respuesta **inmediata** con `job_id` y `status: "pending"`; el procesamiento ocurre en **segundo plano** (cola + workers).
- Cada texto se encola como `TextWorkCommand` (patrón **Command** / productor-consumidor con `queue.Queue`).

## Decisiones técnicas

- **Repository**: abstrae persistencia; existe implementación en memoria (tests) y SQLite (desarrollo).
- **Strategy (hashing)**: interfaz `PasswordHasher` en dominio; implementación bcrypt en infraestructura.
- **AuthService**: lógica de registro/login desacoplada de FastAPI para poder testearla con mocks.
- **Historia #2:** `JobService` persiste el trabajo y, **tras `commit`**, publica comandos en una cola global thread-safe; `WorkerPool` arranca con el ciclo de vida de la app.
- **Historia #3 (hilos vs procesos):** se usan **hilos** + **sesión SQLAlchemy por tarea** y `UPDATE ... RETURNING` / incremento atómico `processed_texts` porque el cuello de botella aquí es I/O (BD + `sleep` simulado) y SQLite compartido entre procesos complica conexiones; el enunciado permite **ThreadPoolExecutor** cuando predomina I/O. `WORKER_COUNT` ≥ 4 cumple paralelismo de consumo de la cola.
- **Historia #4 (CQRS ligero):** lecturas vía `JobQueryRepository` + `JobQueryService`; reporte agregado con **`functools.lru_cache`** por `(user_id, job_id)` una vez el trabajo está `completed` (inmutable). **404** si el `job_id` no existe o **no pertenece** al usuario (sin filtrar existencia).

## Historia #1 — Qué quedó implementado

- **Dominio:** entidad `User`, VOs `Email` y `PlainPassword`, puertos `UserRepository` y `PasswordHasher`, excepciones de dominio.
- **Aplicación:** `AuthService` (registro/login, `threading.RLock`), `JwtService` (HS256, expiración 24 h).
- **Infraestructura:** SQLite + SQLAlchemy (`UserModel`), `SqlAlchemyUserRepository`, `InMemoryUserRepository` (pruebas), `BcryptPasswordHasher`.
- **Presentación:** FastAPI en `app/main.py`, routers de auth y `GET /analyze` protegido, esquemas Pydantic.
- **Pruebas:** `tests/test_auth_service.py` (servicio + JWT).

## Historia #2 — Qué quedó implementado

- **Dominio:** `JobStatus` / `JobTextStatus`, comando `TextWorkCommand`, puertos `JobRepository` y `TextWorkQueuePort`, excepciones de lote vacío o demasiado grande.
- **Aplicación:** `JobService` (persistir + publicar tras commit); el análisis lo consume `ProcessTextService` (Historia #3).
- **Infraestructura:** tablas `jobs` y `job_texts`, `SqlAlchemyJobRepository`, cola `queue.Queue` adaptada a dominio, `WorkerPool` (N hilos, `WORKER_COUNT`).
- **Presentación:** `POST /jobs` con autenticación JWT, **202 Accepted**, esquema `CreateJobRequest` / `CreateJobResponse`.
- **Pruebas:** `tests/test_job_service.py`.

## Reglas de negocio relevantes (Historia #3)

- Cada worker procesa **un texto a la vez** por iteración de bucle.
- Resultado: etiqueta **POSITIVE**, **NEGATIVE** o **NEUTRAL** y **score** en **[-1.0, 1.0]**.
- Fallo (error o **timeout simulado**): texto `failed`, se sigue con el resto; el job pasa a `completed` cuando **todos** los textos están en estado terminal (`completed` o `failed`).
- Avance del job: columnas `total_texts` / `processed_texts` con incremento **atómico** en SQL al cerrar cada texto.

## Historia #3 — Qué quedó implementado

- **Dominio:** `Sentiment`, `analyze_text_sentiment`, `clamp_score` (`app/domain/sentiment.py`).
- **Aplicación:** `AnalysisRuntimeConfig`, `ProcessTextService` (simulación ~50 ms, timeout simulado opcional, idempotencia en completado/fallo).
- **Infraestructura:** columnas `jobs.total_texts` / `jobs.processed_texts` + migración SQLite al arrancar; repositorio con `UPDATE` condicional y cierre de job al alcanzar el total.
- **Arranque:** `configure_worker_analysis(AnalysisRuntimeConfig.from_settings(settings))` antes del `WorkerPool`.
- **Pruebas:** `tests/test_sentiment.py`, `tests/test_process_text_service.py`.
- **Nota:** si tenías un `taller_final.db` antiguo y ves errores raros de esquema, bórralo y reinicia Uvicorn para recrear tablas y aplicar la migración de columnas nuevas.

## Reglas de negocio relevantes (Historia #4)

- Solo el **dueño** del trabajo puede consultar estado, resultados y reporte.
- Con el trabajo en **`processing`** (o `pending`), el **reporte agregado** responde **400**; el **GET** del trabajo sí devuelve progreso (`processed_texts` / `total_texts`).
- Resultados paginados: `page` ≥ 1, `per_page` por defecto 20 y máximo 100.
- Reporte: solo textos **`completed`** con `sentiment` no nulo; promedio de `score` sobre esos textos.

## Historia #4 — Qué quedó implementado

- **Dominio:** read models `OwnedJobView`, `JobTextResultView`, `SentimentReportView`; puerto `JobQueryRepository`; excepciones `JobNotFoundError`, `JobNotReadyForReportError`.
- **Aplicación:** `JobQueryService`, caché LRU en `app/application/report_cache.py`.
- **Infraestructura:** consultas en `SqlAlchemyJobRepository` (join con `jobs` para ownership); agregación SQL con `CASE` / `SUM` / `AVG`.
- **Presentación:** esquemas en `app/presentation/schemas/job_read.py`, rutas en `jobs.py`.
- **Pruebas:** `tests/test_job_query_service.py`.

## Próximos pasos

1. Historia **#5**: WebSocket / webhooks y `JobCompletedEvent`.
2. Historia **#6**: cancelación y cola con prioridad.
3. Ir actualizando la tabla **Estado del proyecto** y esta sección conforme avance cada historia.

## Bitácora

| Fecha | Cambio |
|-------|--------|
| 2026-05-12 | Contraseñas: bcrypt directo vía librería `bcrypt` + pre-hash SHA-256 (evita límite 72 bytes y fallo passlib/bcrypt 5.x). |
| 2026-05-12 | Historia #4: consultas `GET /jobs/{id}`, resultados paginados, reporte + caché LRU, `JobQueryService`. |
| 2026-05-12 | Historia #2: `POST /jobs`, tablas `jobs`/`job_texts`, cola thread-safe, `WorkerPool` al arranque, `ProcessTextService` stub, tests `test_job_service.py`. |
| 2026-05-12 | Añadido `email-validator` en `requirements.txt` (sin él, Uvicorn falla al importar `EmailStr` y el navegador muestra `ERR_CONNECTION_REFUSED`). |
| 2026-05-11 | Scaffold del proyecto, Historia #1 (JWT, registro, login, `/me`, `/analyze`), tests unitarios, documento general. |
