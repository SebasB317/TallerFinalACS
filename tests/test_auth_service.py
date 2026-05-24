import pytest
import asyncio
from app.application.services.auth_service import AuthService
from app.infrastructure.repositories.user_repository_memory import UserRepositoryMemory
from app.infrastructure.security.bcrypt_hasher import BcryptHasher
from app.infrastructure.concurrency.metrics_collector import InMemoryMetricsCollector
from app.domain.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException
)

@pytest.fixture
def auth_service():
    user_repo = UserRepositoryMemory()
    hasher = BcryptHasher()
    metrics = InMemoryMetricsCollector()
    return AuthService(user_repo, hasher, metrics)

@pytest.mark.asyncio
async def test_register_user(auth_service):
    """Test registro de usuario"""
    user = await auth_service.register(
        email="user@example.com",
        password="MyPassword123",
        full_name="Test User"
    )
    
    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.full_name == "Test User"
    assert user.is_active

@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service):
    """Test registro con email duplicado"""
    await auth_service.register(
        email="user@example.com",
        password="MyPassword123"
    )
    
    with pytest.raises(UserAlreadyExistsException):
        await auth_service.register(
            email="user@example.com",
            password="MyPassword123"
        )

@pytest.mark.asyncio
async def test_authenticate_user(auth_service):
    """Test autenticación de usuario"""
    await auth_service.register(
        email="user@example.com",
        password="MyPassword123"
    )
    
    user = await auth_service.authenticate(
        email="user@example.com",
        password="MyPassword123"
    )
    
    assert user.email == "user@example.com"

@pytest.mark.asyncio
async def test_authenticate_wrong_password(auth_service):
    """Test autenticación con contraseña incorrecta"""
    await auth_service.register(
        email="user@example.com",
        password="MyPassword123"
    )
    
    with pytest.raises(InvalidCredentialsException):
        await auth_service.authenticate(
            email="user@example.com",
            password="WrongPassword456"
        )

@pytest.mark.asyncio
async def test_authenticate_nonexistent_user(auth_service):
    """Test autenticación de usuario inexistente"""
    with pytest.raises(UserNotFoundException):
        await auth_service.authenticate(
            email="nonexistent@example.com",
            password="MyPassword123"
        )
