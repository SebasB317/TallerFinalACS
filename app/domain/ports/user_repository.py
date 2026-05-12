from typing import Protocol

from app.domain.entities.user import User
from app.domain.value_objects.email import Email


class UserRepository(Protocol):
    def get_by_email(self, email: Email) -> User | None: ...

    def get_by_id(self, user_id: int) -> User | None: ...

    def save(self, user: User) -> User: ...
