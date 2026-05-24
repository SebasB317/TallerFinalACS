from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/taller_final"
    
    # JWT
    SECRET_KEY: str = "tu-clave-secreta-super-segura-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # API
    API_TITLE: str = "Taller Final - Sistema Distribuido"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Sistema con Arquitectura Limpia: Autenticación, Pagos y Métricas"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
