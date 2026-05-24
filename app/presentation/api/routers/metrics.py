from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from app.presentation.schemas.metrics import MetricsResponse, HealthResponse
from app.domain.ports.metrics_collector import MetricsCollector
from app.presentation.deps import (
    get_metrics_collector,
    get_current_user,
    verify_admin
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    metrics_collector: MetricsCollector = Depends(get_metrics_collector),
    current_user = Depends(get_current_user),
    admin_verified = Depends(verify_admin)
):
    """
    Ejercicio 7: Dashboard administrativo con métricas
    
    Retorna:
    - Pagos procesados y fallidos
    - Monto total en USD
    - Usuarios registrados y logins
    - Intervalo promedio de pagos
    - Estado del sistema (threads activos)
    
    Características:
    - Acceso solo para administradores
    - Thread-safe con RLock
    - Métricas calculadas en tiempo real
    """
    metrics = metrics_collector.get_metrics()
    return MetricsResponse(**metrics)

@router.post("/metrics/reset", status_code=status.HTTP_200_OK)
async def reset_metrics(
    metrics_collector: MetricsCollector = Depends(get_metrics_collector),
    current_user = Depends(get_current_user),
    admin_verified = Depends(verify_admin)
):
    """
    Reiniciar métricas (solo admin)
    """
    metrics_collector.reset_metrics()
    return {"message": "Métricas reiniciadas"}

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check del sistema
    """
    return HealthResponse(
        status="healthy",
        message="Sistema funcionando correctamente",
        timestamp=datetime.utcnow().isoformat()
    )
