from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.entities.payment import Payment
from app.domain.ports.payment_repository import PaymentRepository
from app.infrastructure.database.models import PaymentModel

class PaymentRepositorySQLAlchemy(PaymentRepository):
    """Implementación de PaymentRepository con SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, payment: Payment) -> None:
        """Guardar pago"""
        db_payment = PaymentModel(
            id=payment.id,
            merchant_id=payment.merchant_id,
            amount=payment.amount,
            currency=payment.currency,
            method=payment.method,
            status=payment.status,
            commission=payment.commission,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )
        self.db.add(db_payment)
        self.db.commit()
        self.db.refresh(db_payment)
    
    async def find_by_id(self, payment_id: str) -> Optional[Payment]:
        """Buscar pago por ID"""
        result = self.db.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        db_payment = result.scalars().first()
        return db_payment.to_entity() if db_payment else None
    
    async def update(self, payment: Payment) -> None:
        """Actualizar pago"""
        db_payment = self.db.query(PaymentModel).filter(
            PaymentModel.id == payment.id
        ).first()
        if db_payment:
            db_payment.status = payment.status
            db_payment.commission = payment.commission
            db_payment.updated_at = payment.updated_at
            self.db.commit()
            self.db.refresh(db_payment)
    
    async def find_by_merchant_id(self, merchant_id: str) -> list[Payment]:
        """Buscar pagos por merchant"""
        result = self.db.execute(
            select(PaymentModel).where(PaymentModel.merchant_id == merchant_id)
        )
        db_payments = result.scalars().all()
        return [p.to_entity() for p in db_payments]
