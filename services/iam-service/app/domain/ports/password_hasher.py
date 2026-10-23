from typing import Protocol


class PasswordHasher(Protocol):
    """Deriva y verifica hashes de contraseñas."""

    def hash(self, plain: str) -> str: ...

    def verify(self, plain: str, hashed: str) -> bool: ...
