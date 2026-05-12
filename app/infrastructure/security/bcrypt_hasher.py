import hashlib

import bcrypt

from app.domain.ports.password_hasher import PasswordHasher

_ROUNDS = 12


def _sha256_digest_bytes(plain: str) -> bytes:
    return hashlib.sha256(plain.encode("utf-8")).digest()


class BcryptPasswordHasher:
    """
    Bcrypt con pre-hash SHA-256 (32 bytes) para no topar el límite de 72 bytes de bcrypt.
    Mantiene verificación hacia contraseñas antiguas hasheadas en claro (solo si caben en 72 bytes).
    """

    def hash(self, plain: str) -> str:
        digest = _sha256_digest_bytes(plain)
        return bcrypt.hashpw(digest, bcrypt.gensalt(rounds=_ROUNDS)).decode("ascii")

    def verify(self, plain: str, hashed: str) -> bool:
        h = hashed.encode("ascii")
        digest = _sha256_digest_bytes(plain)
        if bcrypt.checkpw(digest, h):
            return True
        pw = plain.encode("utf-8")
        if len(pw) <= 72:
            try:
                return bool(bcrypt.checkpw(pw, h))
            except ValueError:
                return False
        return False
