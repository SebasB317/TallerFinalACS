import threading
import queue
import time
import random
from typing import Callable, Optional
from app.application.services.payment_service import PaymentService

class PaymentWorker(threading.Thread):
    """
    Worker para procesar pagos de forma asincrónica
    Ejercicio 9: Pagos internacionales - Procesador concurrente
    
    Características:
    - Hereda de threading.Thread para procesamiento concurrente
    - Consume pagos de una cola thread-safe
    - Procesa pagos simulando operaciones (validación antifraude, cálculo de comisión, etc)
    - Actualiza estado en repositorio
    """
    
    def __init__(
        self,
        worker_id: str,
        payment_queue: queue.Queue,
        payment_service: PaymentService,
        stop_event: threading.Event,
        on_payment_processed: Optional[Callable] = None
    ):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.payment_queue = payment_queue
        self.payment_service = payment_service
        self.stop_event = stop_event
        self.on_payment_processed = on_payment_processed
        self.processed_count = 0
    
    def run(self):
        """Ejecutar el worker"""
        print(f"[Worker {self.worker_id}] Iniciado y esperando pagos...")
        
        while not self.stop_event.is_set():
            try:
                # Obtener pago de la cola (timeout para permitir check de stop_event)
                try:
                    payment_id = self.payment_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                try:
                    print(f"[Worker {self.worker_id}] Procesando pago: {payment_id}")
                    
                    # Simular tiempo de procesamiento (antifraude, validación, etc)
                    processing_time = random.uniform(0.2, 0.8)
                    time.sleep(processing_time)
                    
                    # Procesar pago (de forma síncrona)
                    # En producción, usar asyncio.run() o event loop existente
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    payment = loop.run_until_complete(
                        self.payment_service.process_payment(payment_id)
                    )
                    
                    self.processed_count += 1
                    print(f"[Worker {self.worker_id}] ✓ Pago completado: {payment_id}")
                    print(f"  Monto: {payment.amount} {payment.currency}")
                    print(f"  Comisión: {payment.commission} USD")
                    print(f"  Neto: {payment.get_net_amount()} USD")
                    
                    if self.on_payment_processed:
                        self.on_payment_processed(payment)
                    
                except Exception as e:
                    print(f"[Worker {self.worker_id}] ✗ Error procesando pago: {str(e)}")
                finally:
                    self.payment_queue.task_done()
                    
            except Exception as e:
                print(f"[Worker {self.worker_id}] Error inesperado: {str(e)}")
        
        print(f"[Worker {self.worker_id}] Detenido. Procesó {self.processed_count} pagos.")


class PaymentWorkerPool:
    """
    Pool de workers para procesamiento concurrente de pagos
    Patrón: Worker Pool con thread-safe queue
    """
    
    def __init__(
        self,
        num_workers: int,
        queue_size: int,
        payment_service: PaymentService,
        on_payment_processed: Optional[Callable] = None
    ):
        self.num_workers = num_workers
        self.queue_size = queue_size
        self.payment_service = payment_service
        self.on_payment_processed = on_payment_processed
        
        # Cola thread-safe
        self.payment_queue: queue.Queue = queue.Queue(maxsize=queue_size)
        
        # Evento para detener workers
        self.stop_event = threading.Event()
        
        # Lista de workers
        self.workers = []
        
        self._initialize_workers()
    
    def _initialize_workers(self):
        """Inicializar workers"""
        for i in range(self.num_workers):
            worker = PaymentWorker(
                worker_id=f"Worker-{i+1}",
                payment_queue=self.payment_queue,
                payment_service=self.payment_service,
                stop_event=self.stop_event,
                on_payment_processed=self.on_payment_processed
            )
            worker.start()
            self.workers.append(worker)
        
        print(f"✓ Pool de {self.num_workers} workers iniciado")
    
    def enqueue_payment(self, payment_id: str):
        """Encolar pago para procesamiento"""
        try:
            self.payment_queue.put(payment_id, timeout=5)
        except queue.Full:
            raise RuntimeError("Cola de pagos llena. Espere a que se procesen más pagos.")
    
    def wait_all_processed(self):
        """Esperar a que se procesen todos los pagos"""
        print("Esperando a que se procesen todos los pagos...")
        self.payment_queue.join()
        print("✓ Todos los pagos procesados")
    
    def shutdown(self, timeout: int = 10):
        """Detener el pool de workers"""
        print(f"Deteniendo pool de workers (timeout: {timeout}s)...")
        self.stop_event.set()
        
        for worker in self.workers:
            worker.join(timeout=timeout)
            if worker.is_alive():
                print(f"⚠ Worker {worker.worker_id} no se detuvo a tiempo")
        
        print("✓ Pool de workers detenido")
