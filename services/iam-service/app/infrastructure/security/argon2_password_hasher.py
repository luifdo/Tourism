from argon2 import PasswordHasher as _Argon2
from argon2.exceptions import InvalidHashError, VerificationError


class Argon2PasswordHasher:
    """Implementa PasswordHasher con Argon2id y los parámetros por defecto de argon2-cffi."""

    def __init__(self) -> None:
        self._argon2 = _Argon2()

    def hash(self, plain: str) -> str:
        return self._argon2.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return self._argon2.verify(hashed, plain)
        except (VerificationError, InvalidHashError):
            return False

    def needs_rehash(self, hashed: str) -> bool:
        return self._argon2.check_needs_rehash(hashed)
