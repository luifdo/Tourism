"""Publicador en memoria: guarda los sobres en una lista (pruebas y demo sin RabbitMQ)."""

from typing import Any

from domain.eventos import EventoDominio
from infrastructure.messaging.sobre import armar_sobre


class PublicadorMemoria:
    def __init__(self) -> None:
        self.publicados: list[dict[str, Any]] = []

    async def publicar(self, eventos: list[EventoDominio], correlation_id: str | None) -> None:
        self.publicados.extend(armar_sobre(e, correlation_id) for e in eventos)

    def tipos(self) -> list[str]:
        return [s["event_type"] for s in self.publicados]
