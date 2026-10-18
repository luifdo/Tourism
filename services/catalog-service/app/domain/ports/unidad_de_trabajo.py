from types import TracebackType
from typing import Protocol, Self

from app.domain.ports.repositorios import (
    AlertaRepository,
    CalificacionRepository,
    EventosProcesados,
    PrestadorRepository,
    ReservaProyeccionRepository,
    ServicioRepository,
    ZonaRepository,
)


class UnidadDeTrabajo(Protocol):
    """Una transacción sobre catalog_db: los repositorios comparten la misma sesión.

    Al salir del bloque sin `confirmar()` se deshacen los cambios. El outbox se escribe en
    esta misma transacción (paso de mensajería).
    """

    prestadores: PrestadorRepository
    servicios: ServicioRepository
    zonas: ZonaRepository
    alertas: AlertaRepository
    reservas: ReservaProyeccionRepository
    calificaciones: CalificacionRepository
    eventos_procesados: EventosProcesados

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def confirmar(self) -> None: ...
