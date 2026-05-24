import bcrypt
from app.domain.ports.password_hasher import PasswordHasher

class BcryptHasher(PasswordHasher):
    """Implementación de hash con bcrypt"""
    
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
    
    def hash(self, password: str) -> str:
        """Hash de contraseña"""
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def verify(self, password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
