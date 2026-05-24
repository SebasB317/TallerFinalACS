from sqlalchemy.orm import Session
from app.infrastructure.database.base import SessionLocal

async def get_db():
    """Dependency para obtener sesión de BD"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
