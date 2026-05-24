from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import User

class UserRepository(ABC):
    """Puerto para almacenamiento de Usuarios"""
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """Guardar usuario"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Buscar usuario por ID"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Buscar usuario por email"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> None:
        """Eliminar usuario"""
        pass
