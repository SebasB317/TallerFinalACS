import uuid
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException
)
from app.domain.ports.user_repository import UserRepository
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.metrics_collector import MetricsCollector

class AuthService:
    """Servicio de autenticación - Capa de Aplicación"""
    
    def __init__(
        self, 
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        metrics_collector: MetricsCollector
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.metrics_collector = metrics_collector
    
    async def register(self, email: str, password: str, full_name: str = None) -> User:
        """Registrar nuevo usuario"""
        
        # Validar Value Objects
        email_vo = Email(email)
        password_vo = Password(password)
        
        # Verificar que no exista
        existing = await self.user_repository.find_by_email(email)
        if existing:
            raise UserAlreadyExistsException(f"Usuario con email {email} ya existe")
        
        # Hash de la contraseña
        hashed_password = self.password_hasher.hash(password_vo.value)
        
        # Crear entidad
        user = User(
            id=str(uuid.uuid4()),
            email=email_vo.value,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        # Persistir
        await self.user_repository.save(user)
        
        # Registrar métrica
        self.metrics_collector.record_user_registered()
        
        return user
    
    async def authenticate(self, email: str, password: str) -> User:
        """Autenticar usuario"""
        
        # Validar Value Objects
        email_vo = Email(email)
        
        # Buscar usuario
        user = await self.user_repository.find_by_email(email_vo.value)
        if not user:
            raise UserNotFoundException(f"Usuario no encontrado: {email}")
        
        # Verificar contraseña
        if not self.password_hasher.verify(password, user.hashed_password):
            raise InvalidCredentialsException("Contraseña incorrecta")
        
        if not user.is_active:
            raise InvalidCredentialsException("Usuario inactivo")
        
        # Registrar métrica
        self.metrics_collector.record_user_login()
        
        return user
    
    async def get_user(self, user_id: str) -> User:
        """Obtener usuario por ID"""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"Usuario no encontrado: {user_id}")
        return user
