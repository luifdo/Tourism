"""Idempotencia en memoria (en producción va en Valkey: `idem:booking:...`, 48 h)."""

import time
from typing import Any

TTL_SEGUNDOS = 48 * 3600


class AlmacenIdempotenciaMemoria:
    def __init__(self, ttl: int = TTL_SEGUNDOS) -> None:
        self._ttl = ttl
        self._datos: dict[str, tuple[float, Any]] = {}

    async def obtener(self, clave: str) -> Any | None:
        guardado = self._datos.get(clave)
        if guardado is None or guardado[0] < time.monotonic():
            self._datos.pop(clave, None)
            return None
        return guardado[1]

    async def guardar(self, clave: str, respuesta: Any) -> None:
        self._datos[clave] = (time.monotonic() + self._ttl, respuesta)
