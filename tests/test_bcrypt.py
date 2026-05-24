import pytest
from app.infrastructure.security.bcrypt_hasher import BcryptHasher

@pytest.fixture
def hasher():
    return BcryptHasher()

def test_hash_password(hasher):
    """Test hash de contraseña"""
    password = "MyPassword123"
    hashed = hasher.hash(password)
    
    # Verificar que no es el mismo valor
    assert hashed != password
    # Verificar que comienza con $2 (formato bcrypt)
    assert hashed.startswith("$2")

def test_verify_correct_password(hasher):
    """Test verificación de contraseña correcta"""
    password = "MyPassword123"
    hashed = hasher.hash(password)
    
    assert hasher.verify(password, hashed)

def test_verify_incorrect_password(hasher):
    """Test verificación de contraseña incorrecta"""
    password = "MyPassword123"
    wrong_password = "WrongPassword456"
    hashed = hasher.hash(password)
    
    assert not hasher.verify(wrong_password, hashed)
