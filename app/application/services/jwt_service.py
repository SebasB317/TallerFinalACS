from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import settings


class JwtService:
    def __init__(
        self,
        secret: str | None = None,
        algorithm: str | None = None,
        expire_hours: int | None = None,
    ) -> None:
        self._secret = secret or settings.secret_key
        self._algorithm = algorithm or settings.algorithm
        self._expire_hours = expire_hours or settings.access_token_expire_hours

    def create_access_token(self, subject_user_id: int) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(hours=self._expire_hours)
        payload: dict[str, Any] = {
            "sub": str(subject_user_id),
            "iat": now,
            "exp": expire,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_subject_user_id(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            sub = payload.get("sub")
            if sub is None:
                raise ValueError("Token sin subject")
            return int(sub)
        except (JWTError, ValueError) as e:
            raise ValueError("Token inválido o expirado") from e
