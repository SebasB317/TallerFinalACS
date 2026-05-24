import threading
from datetime import datetime
from typing import Dict, Any
from app.domain.ports.metrics_collector import MetricsCollector

class InMemoryMetricsCollector(MetricsCollector):
    """
    Recolector de métricas en memoria con thread-safety
    Ejercicio 7: Dashboard administrativo con métricas
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._reset_metrics()
    
    def _reset_metrics(self):
        """Reinicializar métricas"""
        self.payments_processed = 0
        self.payments_failed = 0
        self.total_amount_usd = 0.0
        self.users_registered = 0
        self.users_logged_in = 0
        self.start_time = datetime.utcnow()
        self.last_payment_time = None
        self.payment_times = []  # para calcular promedio
    
    def record_payment_processed(self, amount: float, currency: str) -> None:
        """Registrar pago procesado"""
        with self._lock:
            self.payments_processed += 1
            self.total_amount_usd += amount
            self.last_payment_time = datetime.utcnow()
            self.payment_times.append(datetime.utcnow())
    
    def record_payment_failed(self) -> None:
        """Registrar pago fallido"""
        with self._lock:
            self.payments_failed += 1
    
    def record_user_registered(self) -> None:
        """Registrar usuario registrado"""
        with self._lock:
            self.users_registered += 1
    
    def record_user_login(self) -> None:
        """Registrar login de usuario"""
        with self._lock:
            self.users_logged_in += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener todas las métricas"""
        with self._lock:
            now = datetime.utcnow()
            uptime_seconds = (now - self.start_time).total_seconds()
            
            # Calcular promedio de tiempo entre pagos
            avg_payment_interval = None
            if len(self.payment_times) > 1:
                time_diffs = []
                for i in range(1, len(self.payment_times)):
                    diff = (self.payment_times[i] - self.payment_times[i-1]).total_seconds()
                    time_diffs.append(diff)
                if time_diffs:
                    avg_payment_interval = sum(time_diffs) / len(time_diffs)
            
            total_payments = self.payments_processed + self.payments_failed
            success_rate = 0.0
            if total_payments > 0:
                success_rate = (self.payments_processed / total_payments) * 100
            
            return {
                "timestamp": now.isoformat(),
                "uptime_seconds": uptime_seconds,
                "payments": {
                    "processed": self.payments_processed,
                    "failed": self.payments_failed,
                    "total": total_payments,
                    "success_rate_percent": round(success_rate, 2),
                    "total_amount_usd": round(self.total_amount_usd, 2),
                    "last_payment_time": self.last_payment_time.isoformat() if self.last_payment_time else None,
                    "avg_payment_interval_seconds": round(avg_payment_interval, 2) if avg_payment_interval else None
                },
                "users": {
                    "registered": self.users_registered,
                    "logins": self.users_logged_in
                },
                "system": {
                    "thread_count": threading.active_count()
                }
            }
    
    def reset_metrics(self) -> None:
        """Reiniciar métricas"""
        with self._lock:
            self._reset_metrics()
