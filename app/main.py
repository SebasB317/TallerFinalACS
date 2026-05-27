from fastapi import FastAPI, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.infrastructure.database.base import engine, Base
from app.presentation.api.routers import auth, payment, metrics

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear aplicación
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(payment.router)
app.include_router(metrics.router)

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a Taller Final - Arquitectura Cliente Servidor",
        "version": settings.API_VERSION,
        "endpoints": {
            "auth": "/api/v1/auth/register, /api/v1/auth/login",
            "payments": "/api/v1/payments/",
            "admin": "/api/v1/admin/metrics"
        }
    }

@app.get("/docs")
async def swagger_ui():
    """Documentación Swagger"""
    return {"message": "Ir a /docs para documentación interactiva"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
