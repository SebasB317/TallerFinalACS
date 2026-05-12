import pytest

from app.application.services.auth_service import AuthService
from app.application.services.jwt_service import JwtService
from app.domain.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.domain.value_objects.email import Email
from app.infrastructure.repositories.user_repository_memory import InMemoryUserRepository


class FakeHasher:
    def hash(self, plain: str) -> str:
        return "h$" + plain

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == "h$" + plain


@pytest.fixture
def auth() -> AuthService:
    return AuthService(InMemoryUserRepository(), FakeHasher())


def test_register_returns_user_with_id(auth: AuthService) -> None:
    u = auth.register("ana@example.com", "Secret123")
    assert u.id is not None
    assert u.email == Email("ana@example.com")
    assert u.password_hash.startswith("h$")


def test_register_duplicate_email(auth: AuthService) -> None:
    auth.register("ana@example.com", "Secret123")
    with pytest.raises(EmailAlreadyRegisteredError):
        auth.register("ana@example.com", "OtherPass1")


def test_register_weak_password(auth: AuthService) -> None:
    with pytest.raises(ValueError, match="mayúscula"):
        auth.register("ana@example.com", "secret123")


def test_login_success(auth: AuthService) -> None:
    auth.register("ana@example.com", "Secret123")
    u = auth.authenticate("ana@example.com", "Secret123")
    assert u.id is not None


def test_login_wrong_password(auth: AuthService) -> None:
    auth.register("ana@example.com", "Secret123")
    with pytest.raises(InvalidCredentialsError):
        auth.authenticate("ana@example.com", "WrongPass1")


def test_jwt_roundtrip() -> None:
    jwt = JwtService(secret="test-secret-key-32-bytes-minimum!!", expire_hours=24)
    token = jwt.create_access_token(42)
    assert jwt.decode_subject_user_id(token) == 42
