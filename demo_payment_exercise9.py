"""
Ejercicio 9: Pagos Internacionales
Demostración del sistema de procesamiento concurrente de pagos

Características:
- Cola thread-safe con capacidad máxima
- N=3 workers procesando concurrentemente
- Validación antifraude simulada
- Cálculo de comisión por método
- Conversión de monedas
- Métricas en tiempo real
"""

import threading
import queue
import time
import random
import asyncio
from decimal import Decimal
from dataclasses import dataclass
from typing import List

# Importar del proyecto
from app.application.services.payment_service import PaymentService
from app.infrastructure.repositories.payment_repository_sqlalchemy import PaymentRepositorySQLAlchemy
from app.infrastructure.concurrency.metrics_collector import InMemoryMetricsCollector
from app.infrastructure.workers.payment_worker import PaymentWorkerPool
from app.domain.constants import PaymentMethod


@dataclass
class PaymentRequest:
    """Solicitud de pago de simulación"""
    merchant_id: str
    amount: Decimal
    currency: str
    method: str


def simulate_payment_producers(
    num_producers: int,
    payments_per_producer: int,
    worker_pool: PaymentWorkerPool,
    payment_service: PaymentService
):
    """
    Simular N productores generando solicitudes de pago
    
    Args:
        num_producers: Número de productores (tiendas en línea)
        payments_per_producer: Pagos por productor
        worker_pool: Pool de workers
        payment_service: Servicio de pagos
    """
    
    def producer_thread(producer_id: int):
        """Thread productor"""
        print(f"\n[Productor {producer_id}] Iniciado")
        
        for i in range(payments_per_producer):
            # Generar pago aleatorio
            merchants = [f"MERCHANT_{100+producer_id}", f"STORE_{producer_id}"]
            currencies = ["USD", "EUR", "GBP", "JPY"]
            methods = ["card", "bank_transfer", "wallet"]
            
            payment_req = PaymentRequest(
                merchant_id=random.choice(merchants),
                amount=Decimal(str(random.uniform(10, 500))).quantize(Decimal("0.01")),
                currency=random.choice(currencies),
                method=random.choice(methods)
            )
            
            try:
                # Crear pago (sincrónico para la demo)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                payment = loop.run_until_complete(
                    payment_service.create_payment(
                        merchant_id=payment_req.merchant_id,
                        amount=payment_req.amount,
                        currency=payment_req.currency,
                        method=payment_req.method
                    )
                )
                
                print(f"[Productor {producer_id}] Encolando pago: "
                      f"{payment_req.merchant_id} | "
                      f"{payment_req.amount} {payment_req.currency}")
                
                # Encolar para procesamiento
                worker_pool.enqueue_payment(payment.id)
                
                # Simular tiempo entre solicitudes
                time.sleep(random.uniform(0.1, 0.5))
                
            except Exception as e:
                print(f"[Productor {producer_id}] Error: {e}")
        
        print(f"[Productor {producer_id}] Completado")
    
    # Iniciar threads productores
    threads = []
    for i in range(num_producers):
        t = threading.Thread(
            target=producer_thread,
            args=(i+1,),
            name=f"Productor-{i+1}"
        )
        t.start()
        threads.append(t)
    
    # Esperar a que terminen
    for t in threads:
        t.join()
    
    print("\n✓ Todos los productores han completado sus entregas")


def print_metrics(metrics_collector: InMemoryMetricsCollector):
    """Imprimir métricas del sistema"""
    metrics = metrics_collector.get_metrics()
    
    print("\n" + "="*60)
    print("MÉTRICAS DEL SISTEMA")
    print("="*60)
    print(f"Timestamp: {metrics['timestamp']}")
    print(f"Uptime: {metrics['uptime_seconds']:.2f}s")
    print("\nPagos:")
    print(f"  - Procesados: {metrics['payments']['processed']}")
    print(f"  - Fallidos: {metrics['payments']['failed']}")
    print(f"  - Total: {metrics['payments']['total']}")
    print(f"  - Tasa de éxito: {metrics['payments']['success_rate_percent']}%")
    print(f"  - Monto total USD: ${metrics['payments']['total_amount_usd']:.2f}")
    if metrics['payments']['avg_payment_interval_seconds']:
        print(f"  - Intervalo promedio: {metrics['payments']['avg_payment_interval_seconds']:.2f}s")
    print("\nUsuarios:")
    print(f"  - Registrados: {metrics['users']['registered']}")
    print(f"  - Logins: {metrics['users']['logins']}")
    print("\nSistema:")
    print(f"  - Threads activos: {metrics['system']['thread_count']}")
    print("="*60 + "\n")


def run_demo():
    """
    Ejecutar demostración completa del Ejercicio 9
    """
    print("\n" + "="*60)
    print("EJERCICIO 9: PAGOS INTERNACIONALES")
    print("="*60)
    print("Sistema de procesamiento concurrente de pagos")
    print("Arquitectura: Productor-Consumidor con Workers")
    print("="*60 + "\n")
    
    # Crear servicios
    metrics_collector = InMemoryMetricsCollector()
    
    # Nota: En una ejecución real, habría repo con DB
    # Para demo, se usa mock
    from unittest.mock import Mock, AsyncMock
    
    payment_repo = Mock()
    payment_repo.save = AsyncMock()
    payment_repo.update = AsyncMock()
    payment_repo.find_by_id = AsyncMock()
    
    payment_service = PaymentService(payment_repo, metrics_collector)
    
    # Crear pool de workers
    print("Inicializando pool de workers...")
    worker_pool = PaymentWorkerPool(
        num_workers=3,
        queue_size=20,
        payment_service=payment_service,
        on_payment_processed=lambda p: print(f"  ✓ Pago procesado: {p.merchant_id}")
    )
    
    # Simular productores
    print("\nIniciando productores...\n")
    simulate_payment_producers(
        num_producers=2,
        payments_per_producer=5,
        worker_pool=worker_pool,
        payment_service=payment_service
    )
    
    # Esperar a que se procesen todos
    worker_pool.wait_all_processed()
    
    # Mostrar métricas
    print_metrics(metrics_collector)
    
    # Detener pool
    worker_pool.shutdown()
    
    print("✓ Demostración completada\n")


if __name__ == "__main__":
    # Para correr: python demo_payment.py
    run_demo()
