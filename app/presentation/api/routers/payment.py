from fastapi import APIRouter, Depends, HTTPException, status
from app.presentation.schemas.payment import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentStatusResponse
)
from app.application.services.payment_service import PaymentService
from app.domain.exceptions import (
    PaymentValidationException,
    PaymentProcessingException
)
from app.presentation.deps import (
    get_payment_service,
    get_current_user
)

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: CreatePaymentRequest,
    payment_service: PaymentService = Depends(get_payment_service),
    current_user = Depends(get_current_user)
):
    """
    Ejercicio 9: Crear solicitud de pago
    
    - Valida merchant_id, monto, moneda y método
    - Crea entidad Payment en BD
    - Encola para procesamiento asincrónico
    """
    try:
        payment = await payment_service.create_payment(
            merchant_id=request.merchant_id,
            amount=request.amount,
            currency=request.currency,
            method=request.method
        )
        return PaymentResponse(
            id=payment.id,
            merchant_id=payment.merchant_id,
            amount=payment.amount,
            currency=payment.currency,
            method=payment.method.value,
            status=payment.status.value,
            commission=payment.commission,
            created_at=payment.created_at.isoformat(),
            updated_at=payment.updated_at.isoformat()
        )
    except PaymentValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    payment_service: PaymentService = Depends(get_payment_service),
    current_user = Depends(get_current_user)
):
    """
    Ejercicio 9: Consultar estado de pago
    """
    payment = await payment_service.payment_repository.find_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    
    return PaymentStatusResponse(
        payment_id=payment.id,
        status=payment.status.value,
        amount=payment.amount,
        currency=payment.currency,
        commission=payment.commission,
        net_amount=payment.get_net_amount()
    )
