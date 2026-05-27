import threading
from typing import Optional

class ReadWriteLock:
    """
    Read-Write Lock con prioridad a escritores
    
    Permite:
    - Múltiples lectores simultáneamente
    - Un solo escritor a la vez (exclusión mutua con lectores)
    - Prioridad a escritores: nuevos lectores esperan si hay escritores pendientes
    
    Ejercicio 9, Parte 2: Sincronización con prioridad a escritores
    """
    
    def __init__(self):
        self._read_count = 0
        self._write_count = 0
        self._lock = threading.Lock()
        self._readers_ok = threading.Condition(self._lock)
        self._writers_ok = threading.Condition(self._lock)
    
    def acquire_read(self, reader_id: Optional[str] = None):
        """Adquirir lock de lectura"""
        self._readers_ok.acquire()
        try:
            # Esperar si hay escritores
            while self._write_count > 0:
                self._readers_ok.wait()
            
            self._read_count += 1
            if reader_id:
                print(f"[LECTOR {reader_id}] Adquirió lectura (total lectores: {self._read_count})")
        finally:
            self._readers_ok.release()
    
    def release_read(self, reader_id: Optional[str] = None):
        """Liberar lock de lectura"""
        self._readers_ok.acquire()
        try:
            self._read_count -= 1
            if reader_id:
                print(f"[LECTOR {reader_id}] Liberó lectura (total lectores: {self._read_count})")
            
            # Si es el último lector y hay escritores esperando, notificar
            if self._read_count == 0:
                self._readers_ok.notify_all()
                self._writers_ok.notify_all()
        finally:
            self._readers_ok.release()
    
    def acquire_write(self, writer_id: Optional[str] = None):
        """Adquirir lock de escritura"""
        self._writers_ok.acquire()
        try:
            self._write_count += 1
            
            # Esperar a que no haya lectores
            while self._read_count > 0:
                self._writers_ok.wait()
            
            if writer_id:
                print(f"[ESCRITOR {writer_id}] Adquirió escritura")
        finally:
            self._writers_ok.release()
    
    def release_write(self, writer_id: Optional[str] = None):
        """Liberar lock de escritura"""
        self._writers_ok.acquire()
        try:
            self._write_count -= 1
            
            if writer_id:
                print(f"[ESCRITOR {writer_id}] Liberó escritura")
            
            # Notificar a lectores y escritores
            self._writers_ok.notify_all()
            self._readers_ok.notify_all()
        finally:
            self._writers_ok.release()
