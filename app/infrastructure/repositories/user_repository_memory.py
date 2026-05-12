import threading

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.ports.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """Repositorio en memoria para pruebas."""

    def __init__(self) -> None:
        self._by_email: dict[str, User] = {}
        self._by_id: dict[int, User] = {}
        self._next_id = 1
        self._lock = threading.RLock()

    def get_by_email(self, email: Email) -> User | None:
        with self._lock:
            return self._by_email.get(email.value)

    def get_by_id(self, user_id: int) -> User | None:
        with self._lock:
            return self._by_id.get(user_id)

    def save(self, user: User) -> User:
        with self._lock:
            if user.id is None:
                uid = self._next_id
                self._next_id += 1
                saved = User(id=uid, email=user.email, password_hash=user.password_hash)
            else:
                saved = user
            self._by_email[saved.email.value] = saved
            self._by_id[saved.id] = saved  # type: ignore[arg-type]
            return saved
