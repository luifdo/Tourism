"""Puertos: interfaces que la aplicación necesita y la infraestructura implementa."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Protocol, Self
from uuid import UUID

from domain.disponibilidad import DisponibilidadCupo
from domain.reserva import EstadoReserva, EventoDominio, Reserva
from domain.servicio import ServicioRef


@dataclass(frozen=True)
class FiltroReservas:
    turista_id: UUID | None = None
    prestador_usuario_id: UUID | None = None
    servicio_id: UUID | None = None
    estado: EstadoReserva | None = None
    desde: date | None = None
    hasta: date | None = None
    orden: str = "recientes"  # "recientes" o "expira_en"


class RepositorioServicios(Protocol):
    """Proyección `servicio_ref`, alimentada por `servicio.publicado.v1`."""

    async def obtener(self, servicio_id: UUID) -> ServicioRef | None: ...

    async def varios(self, servicio_ids: list[UUID]) -> dict[UUID, ServicioRef]: ...

    async def guardar(self, servicio: ServicioRef) -> None: ...


class RepositorioReservas(Protocol):
    async def obtener(self, reserva_id: UUID) -> Reserva | None:
        """Lee y bloquea la reserva hasta el fin de la transacción."""

    async def guardar(self, reserva: Reserva) -> None: ...

    async def existe_activa(
        self, turista_id: UUID, servicio_id: UUID, fecha: date, excluir: UUID | None = None
    ) -> bool: ...

    async def listar(
        self, filtro: FiltroReservas, pagina: int, tamano: int
    ) -> tuple[list[Reserva], int]: ...

    async def solicitudes_vencidas(self, ahora: datetime, limite: int) -> list[Reserva]:
        """SOLICITADA con expira_en <= ahora, bloqueadas (FOR UPDATE SKIP LOCKED)."""

    async def por_finalizar(self, hoy: date, limite: int) -> list[Reserva]:
        """CONFIRMADA con fecha_reserva < hoy, bloqueadas (FOR UPDATE SKIP LOCKED)."""


class RepositorioDisponibilidad(Protocol):
    async def obtener(self, servicio_id: UUID, fecha: date) -> DisponibilidadCupo | None:
        """Lee y bloquea la fila del día (SELECT ... FOR UPDATE)."""

    async def guardar(self, dia: DisponibilidadCupo) -> None: ...

    async def rango(self, servicio_id: UUID, desde: date, hasta: date) -> list[DisponibilidadCupo]: ...

    async def lote(self, servicio_ids: list[UUID], fecha: date) -> dict[UUID, DisponibilidadCupo]:
        """Lectura sin bloqueo de varios servicios en una fecha."""


class UnidadDeTrabajo(Protocol):
    servicios: RepositorioServicios
    reservas: RepositorioReservas
    disponibilidad: RepositorioDisponibilidad

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *exc: object) -> None:
        """Si no hubo commit, deshace."""

    async def commit(self) -> None: ...


class FabricaUnidadDeTrabajo(Protocol):
    def __call__(self) -> UnidadDeTrabajo: ...


class PublicadorEventos(Protocol):
    async def publicar(self, eventos: list[EventoDominio], correlation_id: str | None) -> None: ...


class AlmacenIdempotencia(Protocol):
    async def obtener(self, clave: str) -> Any | None: ...

    async def guardar(self, clave: str, respuesta: Any) -> None: ...


class Reloj(Protocol):
    def ahora(self) -> datetime: ...
