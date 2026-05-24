from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from app.config import settings

class JWTService:
    """Servicio de JWT - Capa de Aplicación"""
    
    def __init__(
        self,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = "HS256",
        expiration_hours: int = 24
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
    
    def create_token(self, user_id: str, email: str) -> str:
        """Crear JWT token"""
        payload = {
            "sub": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Dict:
        """Verificar y decodificar JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")
    
    def get_user_id_from_token(self, token: str) -> str:
        """Extraer user_id del token"""
        payload = self.verify_token(token)
        return payload.get("sub")
