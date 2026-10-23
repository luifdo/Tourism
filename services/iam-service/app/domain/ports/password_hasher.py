from typing import Protocol


class PasswordHasher(Protocol):
    """Deriva y verifica hashes de contraseñas."""

    def hash(self, plain: str) -> str: ...

    def verify(self, plain: str, hashed: str) -> bool: ...

    def needs_rehash(self, hashed: str) -> bool:
        """True si el hash se generó con parámetros distintos a los actuales."""
        ...
