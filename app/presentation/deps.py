from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.application.services.job_query_service import JobQueryService
from app.application.services.job_service import JobService
from app.application.services.jwt_service import JwtService
from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.config import settings
from app.infrastructure.concurrency.text_work_queue_adapter import ThreadSafeTextWorkQueue
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.job_repository_sqlalchemy import SqlAlchemyJobRepository
from app.infrastructure.repositories.user_repository_sqlalchemy import SqlAlchemyUserRepository
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher

security = HTTPBearer()

_work_queue_adapter: ThreadSafeTextWorkQueue | None = None


def get_job_work_queue() -> ThreadSafeTextWorkQueue:
    global _work_queue_adapter
    if _work_queue_adapter is None:
        _work_queue_adapter = ThreadSafeTextWorkQueue()
    return _work_queue_adapter


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


def get_jwt_service() -> JwtService:
    return JwtService()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(SqlAlchemyUserRepository(db), BcryptPasswordHasher())


def get_job_query_service(db: Session = Depends(get_db)) -> JobQueryService:
    return JobQueryService(SqlAlchemyJobRepository(db))


def get_job_service(
    db: Session = Depends(get_db),
    queue: ThreadSafeTextWorkQueue = Depends(get_job_work_queue),
) -> JobService:
    return JobService(
        SqlAlchemyJobRepository(db),
        queue,
        max_texts_per_job=settings.max_texts_per_job,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> User:
    try:
        uid = jwt_service.decode_subject_user_id(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    repo = SqlAlchemyUserRepository(db)
    user = repo.get_by_id(uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def http_error_from_domain(exc: Exception) -> HTTPException:
    if isinstance(exc, EmailAlreadyRegisteredError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, InvalidCredentialsError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )
    raise exc
