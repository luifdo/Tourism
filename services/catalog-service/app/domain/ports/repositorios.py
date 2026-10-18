"""Puertos de persistencia. Los implementa infrastructure/persistence con SQLAlchemy + PostGIS.

Solo declaran lo que necesitan las reglas de escritura; las consultas de lectura
(búsqueda, mapa, analítica) tienen sus propios puertos en los pasos que las implementan.
"""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities.alerta_oficial import AlertaOficial
from app.domain.entities.atractivo_servicio import AtractivoServicio
from app.domain.entities.calificacion_resena import CalificacionResena
from app.domain.entities.prestador_perfil import PrestadorPerfil
from app.domain.entities.reserva_proyeccion import ReservaProyeccion
from app.domain.entities.zona import Zona
from app.domain.value_objects.codigo_zona import CodigoZona
from app.domain.value_objects.geo import Coordenada


class PrestadorRepository(Protocol):
    async def obtener(self, prestador_id: UUID) -> PrestadorPerfil | None: ...

    async def obtener_por_usuario(self, usuario_id: UUID) -> PrestadorPerfil | None: ...

    async def guardar(self, perfil: PrestadorPerfil) -> None: ...


class ServicioRepository(Protocol):
    async def obtener(self, servicio_id: UUID) -> AtractivoServicio | None: ...

    async def listar_por_prestador(self, prestador_id: UUID) -> list[AtractivoServicio]: ...

    async def guardar(self, servicio: AtractivoServicio) -> None: ...


class ZonaRepository(Protocol):
    async def obtener(self, zona_id: UUID) -> Zona | None: ...

    async def obtener_por_codigo(self, codigo: CodigoZona) -> Zona | None: ...

    async def zona_de(self, punto: Coordenada) -> UUID | None:
        """Zona activa que contiene el punto (`ST_Covers`), o None."""
        ...

    async def reasignar_servicios(self, zona_id: UUID) -> None:
        """Recalcula la zona de los servicios afectados cuando cambia el polígono."""
        ...

    async def guardar(self, zona: Zona) -> None: ...


class AlertaRepository(Protocol):
    async def obtener(self, alerta_id: UUID) -> AlertaOficial | None: ...

    async def contar_vigentes_de_zona(self, zona_id: UUID, ahora: datetime) -> int: ...

    async def guardar(self, alerta: AlertaOficial) -> None: ...


class ReservaProyeccionRepository(Protocol):
    async def obtener(self, reserva_id: UUID) -> ReservaProyeccion | None: ...

    async def guardar(self, reserva: ReservaProyeccion) -> None: ...


class CalificacionRepository(Protocol):
    async def guardar(self, calificacion: CalificacionResena) -> None:
        """Inserta o actualiza por `resena_id`."""
        ...


class EventosProcesados(Protocol):
    async def registrar(self, event_id: UUID, consumidor: str) -> bool:
        """Registra el evento en la misma transacción que su efecto.

        Devuelve False si ya estaba registrado (duplicado: se reconoce y se descarta).
        """
        ...
