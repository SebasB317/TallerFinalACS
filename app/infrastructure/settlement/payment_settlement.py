import threading
import time
import random
from decimal import Decimal
from typing import List

class PaymentSettlement:
    """
    Liquidación de pagos internacionales con threading.Barrier
    
    Características:
    - 3 hilos procesan conversiones de EUR, GBP, JPY a USD en paralelo
    - threading.Barrier(3) sincroniza los 3 hilos
    - Una vez que todos terminan, se calcula el total consolidado
    
    Ejercicio 9, Parte 3: Sincronización con Barrier
    """
    
    # Tasas de cambio (simuladas)
    EXCHANGE_RATES = {
        "USD": Decimal("1.0"),
        "EUR": Decimal("1.08"),
        "GBP": Decimal("1.25"),
        "JPY": Decimal("0.0067")
    }
    
    def __init__(self):
        self.barrier = threading.Barrier(3)  # 3 hilos
        self.converted_amounts = {}
        self.lock = threading.Lock()
    
    def convert_to_usd(self, currency: str, amounts: List[Decimal], thread_id: str):
        """
        Convertir lista de montos de una moneda a USD
        
        Args:
            currency: Moneda (EUR, GBP, JPY)
            amounts: Lista de montos a convertir
            thread_id: ID del hilo
        """
        print(f"[THREAD {thread_id}] Iniciando conversión de {currency}...")
        
        rate = self.EXCHANGE_RATES[currency]
        total_usd = Decimal("0")
        
        # Simular procesamiento de cada monto
        for i, amount in enumerate(amounts):
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            converted = amount * rate
            total_usd += converted
            print(f"  [{thread_id}] {amount} {currency} → {converted:.2f} USD")
        
        # Guardar resultado
        with self.lock:
            self.converted_amounts[currency] = total_usd
        
        print(f"[THREAD {thread_id}] ✓ Conversión completada. Total: {total_usd:.2f} USD")
        
        # Esperar a que los otros 2 hilos terminen
        print(f"[THREAD {thread_id}] Esperando barrera...")
        self.barrier.wait()
        print(f"[THREAD {thread_id}] ✓ Barrera alcanzada!")
    
    def get_consolidated_total(self) -> Decimal:
        """Obtener total consolidado en USD"""
        return sum(self.converted_amounts.values())
    
    def print_settlement_report(self):
        """Imprimir reporte de liquidación"""
        print("\n" + "="*60)
        print("REPORTE DE LIQUIDACIÓN CONSOLIDADA")
        print("="*60)
        
        for currency, amount in self.converted_amounts.items():
            print(f"  {currency}: {amount:.2f} USD")
        
        total = self.get_consolidated_total()
        print("-" * 60)
        print(f"TOTAL CONSOLIDADO: {total:.2f} USD")
        print("="*60 + "\n")


def run_settlement_test():
    """Ejecutar prueba de liquidación con Barrier"""
    
    # Datos de prueba: montos en cada moneda
    eur_amounts = [Decimal("100"), Decimal("250"), Decimal("150")]
    gbp_amounts = [Decimal("200"), Decimal("75"), Decimal("125")]
    jpy_amounts = [Decimal("10000"), Decimal("15000"), Decimal("5000")]
    
    settlement = PaymentSettlement()
    
    print("\n" + "="*60)
    print("PRUEBA: LIQUIDACIÓN CON THREADING.BARRIER")
    print("="*60)
    print("3 hilos procesarán conversiones en paralelo...")
    print()
    
    # Crear y lanzar 3 hilos
    threads = [
        threading.Thread(
            target=settlement.convert_to_usd,
            args=("EUR", eur_amounts, "EUR-CONVERTER")
        ),
        threading.Thread(
            target=settlement.convert_to_usd,
            args=("GBP", gbp_amounts, "GBP-CONVERTER")
        ),
        threading.Thread(
            target=settlement.convert_to_usd,
            args=("JPY", jpy_amounts, "JPY-CONVERTER")
        )
    ]
    
    # Iniciar hilos
    for thread in threads:
        thread.start()
    
    # Esperar a que terminen
    for thread in threads:
        thread.join()
    
    # Mostrar reporte
    settlement.print_settlement_report()
    
    return settlement


if __name__ == "__main__":
    run_settlement_test()
