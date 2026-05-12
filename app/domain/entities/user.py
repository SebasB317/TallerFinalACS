from dataclasses import dataclass

from app.domain.value_objects.email import Email


@dataclass(slots=True)
class User:
    id: int | None
    email: Email
    password_hash: str
