import bcrypt

from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher


def test_bcrypt_accepts_long_password() -> None:
    h = BcryptPasswordHasher()
    long_pw = "Aa1" + "x" * 200
    hashed = h.hash(long_pw)
    assert h.verify(long_pw, hashed)
    assert not h.verify(long_pw + "!", hashed)


def test_bcrypt_legacy_plain_short_still_verifies() -> None:
    """Hash antiguo: bcrypt de la contraseña en UTF-8 (sin pre-hash)."""
    legacy_hash = bcrypt.hashpw(b"Secret123", bcrypt.gensalt(rounds=12)).decode("ascii")
    assert BcryptPasswordHasher().verify("Secret123", legacy_hash)
