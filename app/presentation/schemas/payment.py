from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class CreatePaymentRequest(BaseModel):
    """Esquema para crear pago"""
    merchant_id: str
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    method: str = Field(..., pattern="^(card|bank_transfer|wallet)$")

class PaymentResponse(BaseModel):
    """Esquema para respuesta de pago"""
    id: str
    merchant_id: str
    amount: Decimal
    currency: str
    method: str
    status: str
    commission: Decimal
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class PaymentStatusResponse(BaseModel):
    """Esquema para estado de pago"""
    payment_id: str
    status: str
    amount: Decimal
    currency: str
    commission: Decimal
    net_amount: Decimal
