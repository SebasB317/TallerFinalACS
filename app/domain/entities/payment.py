from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.domain.constants import PaymentStatus, PaymentMethod

class Payment:
    """Entidad de Pago - Raíz del Agregado"""
    
    def __init__(
        self,
        id: str,
        merchant_id: str,
        amount: Decimal,
        currency: str,
        method: PaymentMethod,
        status: PaymentStatus = PaymentStatus.PENDING,
        commission: Optional[Decimal] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.merchant_id = merchant_id
        self.amount = Decimal(str(amount))
        self.currency = currency
        self.method = method
        self.status = status
        self.commission = Decimal(str(commission or 0))
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def mark_as_processing(self):
        """Marcar pago como en procesamiento"""
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(self, commission: Decimal):
        """Marcar pago como completado"""
        self.status = PaymentStatus.COMPLETED
        self.commission = Decimal(str(commission))
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(self):
        """Marcar pago como fallido"""
        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.utcnow()
    
    def mark_as_cancelled(self):
        """Marcar pago como cancelado"""
        self.status = PaymentStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def get_net_amount(self) -> Decimal:
        """Obtener monto neto después de comisión"""
        return self.amount - self.commission
