from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.orm import Session
from app.infrastructure.database.base import Base
from app.domain.entities.user import User as UserEntity

class UserModel(Base):
    """Modelo SQLAlchemy para Usuario"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_entity(self) -> UserEntity:
        """Convertir modelo a entidad de dominio"""
        return UserEntity(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

from sqlalchemy import Column, String, Numeric, DateTime, func, Enum
from decimal import Decimal
from app.domain.entities.payment import Payment as PaymentEntity
from app.domain.constants import PaymentStatus, PaymentMethod

class PaymentModel(Base):
    """Modelo SQLAlchemy para Pago"""
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), index=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    commission = Column(Numeric(10, 2), default=Decimal("0.00"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_entity(self) -> PaymentEntity:
        """Convertir modelo a entidad de dominio"""
        return PaymentEntity(
            id=self.id,
            merchant_id=self.merchant_id,
            amount=Decimal(str(self.amount)),
            currency=self.currency,
            method=self.method,
            status=self.status,
            commission=Decimal(str(self.commission)),
            created_at=self.created_at,
            updated_at=self.updated_at
        )
