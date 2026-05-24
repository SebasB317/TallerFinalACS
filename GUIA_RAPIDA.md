# 🚀 Guía Rápida - Taller Final

## ⚡ Inicio Rápido (5 minutos)

### Con Docker (Recomendado)

```bash
# 1. Abrir terminal en la carpeta del proyecto
cd "C:\Users\JUAN ZULUAGA\Desktop\ACS\Taller Final"

# 2. Iniciar con Docker Compose
docker-compose up -d

# 3. Verificar que esté corriendo
docker-compose ps

# ✅ La app debe estar en http://localhost:8000
```

### Sin Docker (Requerimientos: PostgreSQL corriendo)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/Scripts/activate  # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Actualizar .env si es necesario
# DATABASE_URL=postgresql://user:password@localhost:5432/taller_final

# 4. Ejecutar
uvicorn app.main:app --reload
```

## 📚 Ejercicios Implementados

### ✅ Ejercicio 1: Autenticación JWT

```bash
# Registrar usuario
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taller.local",
    "password": "Admin123Password",
    "full_name": "Administrador"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taller.local",
    "password": "Admin123Password"
  }'

# Respuesta: Copiar el token en "access_token"
```

### ✅ Ejercicio 7: Métricas

```bash
# Ver métricas (solo admin)
curl -X GET http://localhost:8000/api/v1/admin/metrics \
  -H "Authorization: Bearer {TOKEN_AQUI}"

# Reiniciar métricas
curl -X POST http://localhost:8000/api/v1/admin/metrics/reset \
  -H "Authorization: Bearer {TOKEN_AQUI}"

# Health check (sin autenticación)
curl http://localhost:8000/api/v1/admin/health
```

### ✅ Ejercicio 9: Pagos Internacionales

```bash
# Crear pago
curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Authorization: Bearer {TOKEN_AQUI}" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "MERCHANT_001",
    "amount": 150.50,
    "currency": "EUR",
    "method": "card"
  }'

# Ver estado del pago
curl -X GET http://localhost:8000/api/v1/payments/{PAYMENT_ID} \
  -H "Authorization: Bearer {TOKEN_AQUI}"
```

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Test específico
pytest tests/test_auth_service.py -v

# Con cobertura
pytest --cov=app tests/

# En tiempo real (watch mode)
pytest-watch
```

## 📖 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **README.md**: Documentación completa
- **ARQUITECTURA_LIMPIA.md**: Guía de arquitectura

## 🛑 Detener Servicios

```bash
# Con Docker
docker-compose down

# Con terminal (Ctrl+C)
# Luego desactivar venv
deactivate
```

## 📊 Demostración Ejercicio 9

```bash
# Ejecutar demo de pagos
python demo_payment_exercise9.py
```

Muestra productores generando pagos y 3 workers procesándolos concurrentemente.

## 🔍 Estructura Importante

```
app/
├── domain/           ← Lógica pura (sin dependencias)
├── application/      ← Servicios (orquestación)
├── infrastructure/   ← BD, workers, seguridad
├── presentation/     ← FastAPI, HTTP
└── config.py         ← Variables

tests/               ← Tests unitarios
docker-compose.yml   ← Servicios
Dockerfile           ← Imagen app
```

## 🔑 Usuarios por Defecto

Para acceder a métricas, registra usuario con email `admin@taller.local`:

```json
{
  "email": "admin@taller.local",
  "password": "AdminPass123",
  "full_name": "Administrador"
}
```

## ⚙️ Variables de Entorno Importantes

Editar `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/taller_final
SECRET_KEY=tu-clave-super-segura-cambiar-en-produccion
```

## 🐛 Troubleshooting

### Error de conexión BD

```bash
# Verificar que PostgreSQL está corriendo
docker-compose logs postgres

# O conectar manualmente
psql -U user -d taller_final
```

### ImportError

```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
```

### Puerto ocupado

```bash
# Cambiar puerto en docker-compose.yml
# O:
netstat -ano | findstr :8000
```

## 📱 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar usuario |
| POST | `/api/v1/auth/login` | Login y JWT |
| POST | `/api/v1/payments/` | Crear pago |
| GET | `/api/v1/payments/{id}` | Ver estado pago |
| GET | `/api/v1/admin/metrics` | Ver métricas |
| POST | `/api/v1/admin/metrics/reset` | Reiniciar métricas |
| GET | `/api/v1/admin/health` | Health check |

## 💡 Tips

1. **Ver logs en tiempo real**: `docker-compose logs -f`
2. **Ejecutar comando en container**: `docker-compose exec app bash`
3. **Base de datos**: `docker-compose exec postgres psql -U user -d taller_final`
4. **Limpiar todo**: `docker-compose down -v` (borra BD)

## ✅ Checklist para Entregar

- [ ] Docker Compose corre sin errores
- [ ] Endpoints autenticación funcionan
- [ ] Métricas se registran correctamente
- [ ] Workers procesan pagos concurrentemente
- [ ] Tests pasan todos
- [ ] Documentación clara
- [ ] Código sigue Arquitectura Limpia

---

**¿Necesitas ayuda?** Revisa los archivos:
- README.md → Documentación completa
- ARQUITECTURA_LIMPIA.md → Patrones y principios
- Tests → Ejemplos de uso
