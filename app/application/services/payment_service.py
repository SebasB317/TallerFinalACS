import uuid
from decimal import Decimal
from app.domain.entities.payment import Payment
from app.domain.constants import PaymentStatus, PaymentMethod
from app.domain.ports.payment_repository import PaymentRepository
from app.domain.ports.metrics_collector import MetricsCollector
from app.domain.exceptions import PaymentValidationException, PaymentProcessingException

class PaymentService:
    """Servicio de Pagos - Capa de Aplicación"""
    
    # Tarifas de comisión por método
    COMMISSION_RATES = {
        PaymentMethod.CARD: Decimal("0.05"),      # 5%
        PaymentMethod.BANK_TRANSFER: Decimal("0.02"),  # 2%
        PaymentMethod.WALLET: Decimal("0.01")     # 1%
    }
    
    # Tasas de cambio (simuladas)
    EXCHANGE_RATES = {
        "USD": Decimal("1.0"),
        "EUR": Decimal("1.08"),
        "GBP": Decimal("1.25"),
        "JPY": Decimal("0.0067")
    }
    
    def __init__(
        self,
        payment_repository: PaymentRepository,
        metrics_collector: MetricsCollector
    ):
        self.payment_repository = payment_repository
        self.metrics_collector = metrics_collector
    
    def validate_payment(
        self,
        merchant_id: str,
        amount: Decimal,
        currency: str,
        method: str
    ) -> bool:
        """Validar pago"""
        
        if not merchant_id:
            raise PaymentValidationException("merchant_id requerido")
        
        if amount <= 0:
            raise PaymentValidationException("amount debe ser mayor a 0")
        
        if currency not in self.EXCHANGE_RATES:
            raise PaymentValidationException(f"currency no soportada: {currency}")
        
        try:
            PaymentMethod[method.upper()]
        except KeyError:
            raise PaymentValidationException(f"method no soportado: {method}")
        
        return True
    
    def calculate_commission(self, amount: Decimal, method: PaymentMethod) -> Decimal:
        """Calcular comisión"""
        rate = self.COMMISSION_RATES.get(method, Decimal("0.03"))
        return (amount * rate).quantize(Decimal("0.01"))
    
    def convert_to_usd(self, amount: Decimal, from_currency: str) -> Decimal:
        """Convertir moneda a USD"""
        if from_currency not in self.EXCHANGE_RATES:
            raise PaymentValidationException(f"Moneda no soportada: {from_currency}")
        
        rate = self.EXCHANGE_RATES[from_currency]
        return (amount * rate).quantize(Decimal("0.01"))
    
    async def create_payment(
        self,
        merchant_id: str,
        amount: Decimal,
        currency: str,
        method: str
    ) -> Payment:
        """Crear pago"""
        
        # Validar
        self.validate_payment(merchant_id, amount, currency, method)
        
        # Crear entidad
        payment = Payment(
            id=str(uuid.uuid4()),
            merchant_id=merchant_id,
            amount=Decimal(str(amount)),
            currency=currency,
            method=PaymentMethod[method.upper()]
        )
        
        # Persistir
        await self.payment_repository.save(payment)
        
        return payment
    
    async def process_payment(self, payment_id: str) -> Payment:
        """Procesar pago"""
        
        # Obtener pago
        payment = await self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise PaymentProcessingException(f"Pago no encontrado: {payment_id}")
        
        # Marcar como procesando
        payment.mark_as_processing()
        await self.payment_repository.update(payment)
        
        try:
            # Calcular comisión
            commission = self.calculate_commission(payment.amount, payment.method)
            
            # Convertir a USD si es necesario
            amount_usd = self.convert_to_usd(payment.amount, payment.currency)
            
            # Marcar como completado
            payment.mark_as_completed(commission)
            await self.payment_repository.update(payment)
            
            # Registrar métrica
            self.metrics_collector.record_payment_processed(
                float(amount_usd),
                "USD"
            )
            
            return payment
            
        except Exception as e:
            payment.mark_as_failed()
            await self.payment_repository.update(payment)
            self.metrics_collector.record_payment_failed()
            raise PaymentProcessingException(f"Error procesando pago: {str(e)}")
