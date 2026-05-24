import pytest
from app.domain.value_objects.email import Email
from app.domain.exceptions import InvalidEmailException

def test_valid_email():
    """Test email válido"""
    email = Email("user@example.com")
    assert email.value == "user@example.com"

def test_email_lowercase():
    """Test email convertido a minúsculas"""
    email = Email("USER@EXAMPLE.COM")
    assert email.value == "user@example.com"

def test_invalid_email():
    """Test email inválido"""
    with pytest.raises(InvalidEmailException):
        Email("invalid-email")

def test_invalid_email_no_domain():
    """Test email sin dominio"""
    with pytest.raises(InvalidEmailException):
        Email("user@")
