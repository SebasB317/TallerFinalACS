from decimal import Decimal
import threading
import time
from app.infrastructure.concurrency.read_write_lock import ReadWriteLock

class PaymentConfig:
    """
    Configuración de tasas de cambio con soporte para lectura/escritura concurrente
    
    Características:
    - Lectores: pueden consultar tasas simultáneamente
    - Escritores: exclusión mutua (un escritor a la vez)
    - Prioridad: escritores tienen prioridad sobre nuevos lectores
    
    Ejercicio 9, Parte 2: ReadWriteLock con prioridad a escritores
    """
    
    def __init__(self):
        self._lock = ReadWriteLock()
        self._exchange_rates = {
            "USD": Decimal("1.0"),
            "EUR": Decimal("1.08"),
            "GBP": Decimal("1.25"),
            "JPY": Decimal("0.0067")
        }
    
    def get_rate(self, currency: str, reader_id: str = None) -> Decimal:
        """
        Obtener tasa de cambio (lectura concurrente)
        
        Args:
            currency: Moneda (USD, EUR, GBP, JPY)
            reader_id: ID del lector (para logging)
        
        Returns:
            Tasa de cambio
        """
        self._lock.acquire_read(reader_id)
        try:
            rate = self._exchange_rates.get(currency)
            if reader_id:
                print(f"  [LECTOR {reader_id}] Consultó tasa de {currency}: {rate}")
            return rate
        finally:
            self._lock.release_read(reader_id)
    
    def update_rates(self, updates: dict, writer_id: str = None):
        """
        Actualizar tasas de cambio (escritura exclusiva)
        
        Args:
            updates: Diccionario con tasas a actualizar
            writer_id: ID del escritor (para logging)
        """
        self._lock.acquire_write(writer_id)
        try:
            self._exchange_rates.update(updates)
            if writer_id:
                print(f"  [ESCRITOR {writer_id}] Actualizó tasas: {updates}")
            time.sleep(0.5)  # Simular operación de escritura
        finally:
            self._lock.release_write(writer_id)
    
    def get_all_rates(self) -> dict:
        """Obtener todas las tasas"""
        self._lock.acquire_read()
        try:
            return dict(self._exchange_rates)
        finally:
            self._lock.release_read()
