from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.ports.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: Email) -> User | None:
        row = self._session.scalar(select(UserModel).where(UserModel.email == email.value))
        return self._to_domain(row) if row else None

    def get_by_id(self, user_id: int) -> User | None:
        row = self._session.get(UserModel, user_id)
        return self._to_domain(row) if row else None

    def save(self, user: User) -> User:
        if user.id is None:
            model = UserModel(email=user.email.value, password_hash=user.password_hash)
            self._session.add(model)
            self._session.flush()
            self._session.refresh(model)
            return User(id=model.id, email=Email(model.email), password_hash=model.password_hash)
        model = self._session.get(UserModel, user.id)
        if model is None:
            model = UserModel(id=user.id, email=user.email.value, password_hash=user.password_hash)
            self._session.add(model)
        else:
            model.email = user.email.value
            model.password_hash = user.password_hash
        self._session.flush()
        self._session.refresh(model)
        return User(id=model.id, email=Email(model.email), password_hash=model.password_hash)

    @staticmethod
    def _to_domain(row: UserModel) -> User:
        return User(id=row.id, email=Email(row.email), password_hash=row.password_hash)
