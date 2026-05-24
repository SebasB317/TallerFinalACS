import pytest
from app.domain.value_objects.password import Password
from app.domain.exceptions import InvalidPasswordException

def test_valid_password():
    """Test contraseña válida"""
    password = Password("MyPass123")
    assert password.value == "MyPass123"

def test_invalid_password_too_short():
    """Test contraseña muy corta"""
    with pytest.raises(InvalidPasswordException):
        Password("Short1")

def test_invalid_password_no_uppercase():
    """Test contraseña sin mayúscula"""
    with pytest.raises(InvalidPasswordException):
        Password("password123")

def test_invalid_password_no_number():
    """Test contraseña sin número"""
    with pytest.raises(InvalidPasswordException):
        Password("PasswordTest")
