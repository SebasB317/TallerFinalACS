from pydantic import BaseModel
from typing import Dict, Any, Optional

class MetricsResponse(BaseModel):
    """Esquema para respuesta de métricas"""
    timestamp: str
    uptime_seconds: float
    payments: Dict[str, Any]
    users: Dict[str, Any]
    system: Dict[str, Any]

class HealthResponse(BaseModel):
    """Esquema para health check"""
    status: str
    message: str
    timestamp: str
