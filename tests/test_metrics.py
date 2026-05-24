import pytest
import time
from app.infrastructure.concurrency.metrics_collector import InMemoryMetricsCollector

@pytest.fixture
def metrics_collector():
    return InMemoryMetricsCollector()

def test_record_payment_processed(metrics_collector):
    """Test registrar pago procesado"""
    metrics_collector.record_payment_processed(100.0, "USD")
    metrics_collector.record_payment_processed(50.0, "USD")
    
    metrics = metrics_collector.get_metrics()
    assert metrics["payments"]["processed"] == 2
    assert metrics["payments"]["total_amount_usd"] == 150.0

def test_record_payment_failed(metrics_collector):
    """Test registrar pago fallido"""
    metrics_collector.record_payment_failed()
    metrics_collector.record_payment_failed()
    
    metrics = metrics_collector.get_metrics()
    assert metrics["payments"]["failed"] == 2

def test_record_user_registered(metrics_collector):
    """Test registrar usuario registrado"""
    metrics_collector.record_user_registered()
    metrics_collector.record_user_registered()
    metrics_collector.record_user_registered()
    
    metrics = metrics_collector.get_metrics()
    assert metrics["users"]["registered"] == 3

def test_success_rate(metrics_collector):
    """Test cálculo de tasa de éxito"""
    metrics_collector.record_payment_processed(100.0, "USD")
    metrics_collector.record_payment_processed(100.0, "USD")
    metrics_collector.record_payment_failed()
    
    metrics = metrics_collector.get_metrics()
    # 2 exitosos, 1 fallido = 66.67%
    assert metrics["payments"]["success_rate_percent"] == 66.67

def test_reset_metrics(metrics_collector):
    """Test reiniciar métricas"""
    metrics_collector.record_payment_processed(100.0, "USD")
    metrics_collector.record_user_registered()
    
    metrics_collector.reset_metrics()
    
    metrics = metrics_collector.get_metrics()
    assert metrics["payments"]["processed"] == 0
    assert metrics["users"]["registered"] == 0

def test_thread_safety(metrics_collector):
    """Test thread-safety de métricas"""
    import threading
    
    def record_payments(count):
        for _ in range(count):
            metrics_collector.record_payment_processed(10.0, "USD")
    
    threads = [
        threading.Thread(target=record_payments, args=(100,))
        for _ in range(5)
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    metrics = metrics_collector.get_metrics()
    # 5 threads * 100 pagos = 500
    assert metrics["payments"]["processed"] == 500
