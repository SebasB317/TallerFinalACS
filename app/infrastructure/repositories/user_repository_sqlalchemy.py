from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.domain.entities.user import User
from app.domain.ports.user_repository import UserRepository
from app.infrastructure.database.models import UserModel

class UserRepositorySQLAlchemy(UserRepository):
    """Implementación de UserRepository con SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, user: User) -> None:
        """Guardar usuario"""
        db_user = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Buscar usuario por ID"""
        result = self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalars().first()
        return db_user.to_entity() if db_user else None
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Buscar usuario por email"""
        result = self.db.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        db_user = result.scalars().first()
        return db_user.to_entity() if db_user else None
    
    async def delete(self, user_id: str) -> None:
        """Eliminar usuario"""
        self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
