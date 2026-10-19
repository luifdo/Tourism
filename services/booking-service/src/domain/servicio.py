"""Proyección local de un servicio del catálogo (`servicio_ref`, Guía §8).

La alimenta el evento `servicio.publicado.v1`; booking nunca la modifica por su API.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain import reglas
from domain.disponibilidad import DisponibilidadCupo
from domain.errores import NoDisponible


@dataclass
class ServicioRef:
    servicio_id: UUID
    prestador_id: UUID  # perfil del prestador en el catálogo; viaja en los eventos reserva.*
    prestador_usuario_id: UUID  # usuario en iam; coincide con X-Usuario-Id
    capacidad_aforo_diario: int
    tarifa_base: Decimal
    activo: bool
    version: int

    def es_de(self, usuario_id: UUID) -> bool:
        return self.prestador_usuario_id == usuario_id

    def exigir_activo(self) -> None:
        if not self.activo:
            raise NoDisponible("El servicio no está activo en el catálogo.")

    def reemplaza_a(self, actual: "ServicioRef | None") -> bool:
        """Un evento solo se aplica si es más nuevo que lo guardado (descarta viejos y repetidos)."""
        return actual is None or self.version > actual.version


def disponibilidad_en(
    servicio: ServicioRef | None,
    dia: DisponibilidadCupo | None,
    fecha: date,
    personas: int,
    ahora: datetime,
) -> tuple[int, bool]:
    """Cupos y si se puede solicitar: servicio activo, día abierto, fecha a partir de mañana
    y cupos suficientes (lote de disponibilidad para /buscar del catálogo)."""
    if servicio is None or not servicio.activo or dia is None:
        return 0, False
    cupos = dia.cupos_disponibles
    admite_solicitudes = fecha > reglas.hoy_local(ahora)
    return cupos, admite_solicitudes and cupos >= personas
