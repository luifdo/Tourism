from typing import Protocol

from app.domain.entities.usuario import Usuario
from app.domain.value_objects.email import Email


class UsuarioRepository(Protocol):
    async def add(self, usuario: Usuario) -> Usuario:
        """Persiste el usuario y lo devuelve con id y timestamps.

        Lanza UsuarioYaExisteError si el email ya está registrado.
        """
        ...

    async def find_by_email(self, email: Email) -> Usuario | None: ...
