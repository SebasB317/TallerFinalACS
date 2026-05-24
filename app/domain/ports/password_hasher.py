from abc import ABC, abstractmethod

class PasswordHasher(ABC):
    """Puerto para hash de contraseñas"""
    
    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash de contraseña"""
        pass
    
    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        pass
