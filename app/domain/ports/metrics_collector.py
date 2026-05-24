from abc import ABC, abstractmethod
from typing import Dict, Any

class MetricsCollector(ABC):
    """Puerto para recolección de métricas"""
    
    @abstractmethod
    def record_payment_processed(self, amount: float, currency: str) -> None:
        """Registrar pago procesado"""
        pass
    
    @abstractmethod
    def record_payment_failed(self) -> None:
        """Registrar pago fallido"""
        pass
    
    @abstractmethod
    def record_user_registered(self) -> None:
        """Registrar usuario registrado"""
        pass
    
    @abstractmethod
    def record_user_login(self) -> None:
        """Registrar login de usuario"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener todas las métricas"""
        pass
    
    @abstractmethod
    def reset_metrics(self) -> None:
        """Reiniciar métricas"""
        pass
