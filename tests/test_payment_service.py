import pytest
from decimal import Decimal
from app.application.services.payment_service import PaymentService
from app.infrastructure.repositories.payment_repository_sqlalchemy import PaymentRepositorySQLAlchemy
from app.infrastructure.concurrency.metrics_collector import InMemoryMetricsCollector
from app.domain.constants import PaymentMethod
from app.domain.exceptions import PaymentValidationException
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def payment_service():
    payment_repo = Mock(spec=PaymentRepositorySQLAlchemy)
    metrics = InMemoryMetricsCollector()
    return PaymentService(payment_repo, metrics)

def test_validate_payment_valid(payment_service):
    """Test validación de pago válido"""
    assert payment_service.validate_payment(
        merchant_id="merchant_123",
        amount=Decimal("100.00"),
        currency="USD",
        method="card"
    )

def test_validate_payment_invalid_amount(payment_service):
    """Test validación de pago con monto inválido"""
    with pytest.raises(PaymentValidationException):
        payment_service.validate_payment(
            merchant_id="merchant_123",
            amount=Decimal("0"),
            currency="USD",
            method="card"
        )

def test_validate_payment_invalid_currency(payment_service):
    """Test validación de pago con moneda no soportada"""
    with pytest.raises(PaymentValidationException):
        payment_service.validate_payment(
            merchant_id="merchant_123",
            amount=Decimal("100.00"),
            currency="XYZ",
            method="card"
        )

def test_calculate_commission(payment_service):
    """Test cálculo de comisión"""
    commission = payment_service.calculate_commission(
        Decimal("100.00"),
        PaymentMethod.CARD
    )
    assert commission == Decimal("5.00")

def test_convert_to_usd(payment_service):
    """Test conversión de moneda a USD"""
    usd_amount = payment_service.convert_to_usd(
        Decimal("100.00"),
        "EUR"
    )
    # EUR rate is 1.08, so 100 * 1.08 = 108
    assert usd_amount == Decimal("108.00")
