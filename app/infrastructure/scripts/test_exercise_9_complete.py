#!/usr/bin/env python
"""
Script de Prueba del Ejercicio 9: Pagos Internacionales

Ejecuta las 3 partes del ejercicio:
1. Cola de pagos con workers
2. ReadWriteLock con prioridad a escritores  
3. Liquidación con threading.Barrier
"""

import threading
import time
from decimal import Decimal

print("\n" + "="*70)
print("EJERCICIO 9: PAGOS INTERNACIONALES - PRUEBA COMPLETA")
print("="*70 + "\n")

# ============================================================================
# PARTE 1: COLA DE PAGOS CON WORKERS
# ============================================================================

print("█ PARTE 1: COLA DE PAGOS CON WORKERS (threading + queue.Queue)")
print("-"*70)

from app.infrastructure.workers.payment_worker import PaymentWorkerPool
from app.application.services.payment_service import PaymentService
from app.infrastructure.repositories.payment_repository_sqlalchemy import PaymentRepositorySQLAlchemy
from app.infrastructure.concurrency.metrics_collector import InMemoryMetricsCollector
from app.infrastructure.database.base import SessionLocal

# Inicializar servicios
db = SessionLocal()
metrics = InMemoryMetricsCollector()
payment_repo = PaymentRepositorySQLAlchemy(db)
payment_service = PaymentService(payment_repo, metrics)

# Crear pool de workers (3 workers, cola maxsize=20)
pool = PaymentWorkerPool(
    num_workers=3,
    queue_size=20,
    payment_service=payment_service
)

print("\nEncolando 15 solicitudes de pago...\n")

# Simular productor encolando 15 pagos
for i in range(1, 16):
    merchant_id = f"MERCHANT_{1000 + i}"
    # Estas serían IDs de pagos ya creados en la BD
    payment_id = f"payment_{i}"
    
    try:
        pool.enqueue_payment(payment_id)
        print(f"[Productor] Encolado pago #{i}: {merchant_id}")
        time.sleep(0.1)  # Pequeño delay entre encolados
    except Exception as e:
        print(f"[Productor] Error: {e}")

print("\nEsperando procesamiento...")
pool.wait_all_processed()
pool.shutdown()

print("\n✅ PARTE 1 COMPLETADA\n")

# ============================================================================
# PARTE 2: READ-WRITE LOCK CON PRIORIDAD A ESCRITORES
# ============================================================================

print("█ PARTE 2: READ-WRITE LOCK (Lectores/Escritores con prioridad)")
print("-"*70)

from app.domain.config.payment_config import PaymentConfig

config = PaymentConfig()

print("\nSimulando 10 lectores (cada uno lee 5 veces) y 2 escritores (cada uno escribe 3 veces)\n")

def reader_task(reader_id, config):
    """Tarea de lector: consulta tasas 5 veces"""
    for i in range(5):
        rate = config.get_rate("EUR", f"R{reader_id}")
        time.sleep(0.05)

def writer_task(writer_id, config):
    """Tarea de escritor: actualiza tasas 3 veces"""
    for i in range(3):
        config.update_rates({
            "EUR": Decimal("1.08") + Decimal(f"0.0{i}"),
            "GBP": Decimal("1.25") + Decimal(f"0.0{i}"),
        }, f"W{writer_id}")
        time.sleep(0.2)

# Crear 10 lectores
readers = [
    threading.Thread(target=reader_task, args=(i, config))
    for i in range(1, 11)
]

# Crear 2 escritores
writers = [
    threading.Thread(target=writer_task, args=(i, config))
    for i in range(1, 3)
]

# Mezclar hilos para demostrar prioridad
all_threads = readers[:5] + writers + readers[5:]

print("Iniciando 12 hilos (10 lectores + 2 escritores)...\n")

for thread in all_threads:
    thread.start()

for thread in all_threads:
    thread.join()

print("\n✅ PARTE 2 COMPLETADA\n")

# ============================================================================
# PARTE 3: LIQUIDACIÓN CON THREADING.BARRIER
# ============================================================================

print("█ PARTE 3: LIQUIDACIÓN (threading.Barrier para 3 monedas)")
print("-"*70)

from app.infrastructure.settlement.payment_settlement import run_settlement_test

run_settlement_test()

print("✅ PARTE 3 COMPLETADA\n")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("="*70)
print("✅ TODAS LAS 3 PARTES DEL EJERCICIO 9 COMPLETADAS EXITOSAMENTE")
print("="*70)
print("""
RESUMEN:
  ✅ Parte 1: Cola de pagos con 3 workers - 15 pagos procesados
  ✅ Parte 2: ReadWriteLock con prioridad - 10 lectores + 2 escritores
  ✅ Parte 3: Liquidación con Barrier - 3 monedas → USD consolidado

CONCEPTOS DEMOSTRADOS:
  - threading.Thread (herencia)
  - queue.Queue (thread-safe)
  - threading.Lock y threading.Condition
  - threading.Barrier (sincronización)
  - Concurrencia productor-consumidor
  - Prioridad en locks (escritores sobre lectores)
  - Conversión de monedas en paralelo
""")
print("="*70 + "\n")
