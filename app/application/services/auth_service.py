import threading

from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import PlainPassword


class AuthService:
    """Servicio de autenticación; RLock para operaciones no atómicas en memoria."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        self._users = users
        self._hasher = hasher
        self._lock = threading.RLock()

    def register(self, email: str, password: str) -> User:
        em = Email(email)
        pw = PlainPassword(password)
        with self._lock:
            if self._users.get_by_email(em) is not None:
                raise EmailAlreadyRegisteredError("El email ya está registrado.")
            hashed = self._hasher.hash(pw.value)
            user = User(id=None, email=em, password_hash=hashed)
            return self._users.save(user)

    def authenticate(self, email: str, password: str) -> User:
        em = Email(email)
        with self._lock:
            user = self._users.get_by_email(em)
            if user is None or not self._hasher.verify(password, user.password_hash):
                raise InvalidCredentialsError("Credenciales inválidas.")
            return user
