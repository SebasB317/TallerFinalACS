from typing import Optional, Dict
from app.domain.entities.user import User
from app.domain.ports.user_repository import UserRepository

class UserRepositoryMemory(UserRepository):
    """Implementación en memoria de UserRepository para pruebas"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.email_index: Dict[str, str] = {}
    
    async def save(self, user: User) -> None:
        """Guardar usuario en memoria"""
        self.users[user.id] = user
        self.email_index[user.email] = user.id
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Buscar usuario por ID"""
        return self.users.get(user_id)
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Buscar usuario por email"""
        user_id = self.email_index.get(email.lower())
        if user_id:
            return self.users.get(user_id)
        return None
    
    async def delete(self, user_id: str) -> None:
        """Eliminar usuario"""
        if user_id in self.users:
            user = self.users[user_id]
            del self.email_index[user.email]
            del self.users[user_id]
