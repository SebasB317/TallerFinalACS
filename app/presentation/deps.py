from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.services.auth_service import AuthService
from app.application.services.jwt_service import JWTService
from app.application.services.payment_service import PaymentService
from app.infrastructure.repositories.user_repository_sqlalchemy import UserRepositorySQLAlchemy
from app.infrastructure.repositories.payment_repository_sqlalchemy import PaymentRepositorySQLAlchemy
from app.infrastructure.security.bcrypt_hasher import BcryptHasher
from app.domain.ports.metrics_collector import MetricsCollector
from app.infrastructure.concurrency.metrics_collector import InMemoryMetricsCollector

# Instancia global de métricas
_metrics_collector: MetricsCollector = InMemoryMetricsCollector()

def get_metrics_collector() -> MetricsCollector:
    """Obtener recolector de métricas global"""
    return _metrics_collector

def get_password_hasher() -> BcryptHasher:
    """Obtener hasher de contraseñas"""
    return BcryptHasher()

def get_jwt_service() -> JWTService:
    """Obtener servicio de JWT"""
    return JWTService()

async def get_auth_service(
    db: Session = Depends(get_db),
    password_hasher = Depends(get_password_hasher),
    metrics = Depends(get_metrics_collector)
) -> AuthService:
    """Obtener servicio de autenticación"""
    user_repo = UserRepositorySQLAlchemy(db)
    return AuthService(user_repo, password_hasher, metrics)

async def get_payment_service(
    db: Session = Depends(get_db),
    metrics = Depends(get_metrics_collector)
) -> PaymentService:
    """Obtener servicio de pagos"""
    payment_repo = PaymentRepositorySQLAlchemy(db)
    return PaymentService(payment_repo, metrics)

async def get_current_user(
    authorization: str = None,
    jwt_service: JWTService = Depends(get_jwt_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Obtener usuario actual desde el token JWT
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autenticación inválido"
            )
        
        user_id = jwt_service.get_user_id_from_token(token)
        user = await auth_service.get_user(user_id)
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

async def verify_admin(current_user = Depends(get_current_user)):
    """
    Verificar que el usuario sea administrador
    (Para esta demo, verificar por email específico)
    """
    admin_emails = ["admin@taller.local", "administrador@taller.local"]
    if current_user.email.lower() not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a este recurso"
        )
    return current_user
