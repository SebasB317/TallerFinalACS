from typing import Optional
from datetime import datetime

class User:
    """Entidad de Usuario - Raíz del Agregado"""
    
    def __init__(
        self, 
        id: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def deactivate(self):
        """Desactivar usuario"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activar usuario"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_password(self, new_hashed_password: str):
        """Actualizar contraseña"""
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.utcnow()
