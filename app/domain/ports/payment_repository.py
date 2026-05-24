from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.payment import Payment

class PaymentRepository(ABC):
    """Puerto para almacenamiento de Pagos"""
    
    @abstractmethod
    async def save(self, payment: Payment) -> None:
        """Guardar pago"""
        pass
    
    @abstractmethod
    async def find_by_id(self, payment_id: str) -> Optional[Payment]:
        """Buscar pago por ID"""
        pass
    
    @abstractmethod
    async def update(self, payment: Payment) -> None:
        """Actualizar pago"""
        pass
    
    @abstractmethod
    async def find_by_merchant_id(self, merchant_id: str) -> list[Payment]:
        """Buscar pagos por merchant"""
        pass
