from datetime import datetime
from typing import Protocol


class RevocacionTokens(Protocol):
    """Lista de tokens revocados por jti.

    Lanza ServicioNoDisponibleError si no puede comprobarlo: nunca asume "no revocado".
    """

    async def revocar(self, jti: str, expira_en: datetime) -> None: ...

    async def esta_revocado(self, jti: str) -> bool: ...
