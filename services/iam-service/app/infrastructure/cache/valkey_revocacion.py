import logging
import math
from collections.abc import Callable
from datetime import datetime

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.domain.exceptions import ServicioNoDisponibleError

logger = logging.getLogger(__name__)

PREFIJO = "iam:revoked:"
_FALLAS_DE_CONEXION = (RedisConnectionError, RedisTimeoutError, ConnectionError, TimeoutError)


def build_valkey_client(valkey_url: str) -> Redis:
    # Timeouts cortos: si Valkey no responde, el logout debe fallar rápido con 503.
    return Redis.from_url(valkey_url, socket_connect_timeout=2, socket_timeout=2)


class ValkeyRevocacionTokens:
    """Implementa RevocacionTokens en Valkey. Falla cerrado: sin respuesta, no hay "no revocado"."""

    def __init__(self, client: Redis, reloj: Callable[[], datetime]) -> None:
        self._client = client
        self._reloj = reloj

    async def revocar(self, jti: str, expira_en: datetime) -> None:
        # La llave vive lo mismo que el token: después de exp ya no hace falta recordarla.
        ttl = max(1, math.ceil((expira_en - self._reloj()).total_seconds()))
        try:
            await self._client.set(PREFIJO + jti, "1", ex=ttl)
        except _FALLAS_DE_CONEXION as exc:
            logger.warning("Valkey no responde al revocar el jti %s…", jti[:8])
            raise ServicioNoDisponibleError() from exc

    async def esta_revocado(self, jti: str) -> bool:
        try:
            return await self._client.exists(PREFIJO + jti) > 0
        except _FALLAS_DE_CONEXION as exc:
            logger.warning("Valkey no responde al consultar el jti %s…", jti[:8])
            raise ServicioNoDisponibleError() from exc
