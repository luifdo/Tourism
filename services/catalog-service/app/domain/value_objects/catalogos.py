"""Valores fijos del dominio. Se exponen como códigos estables; la PWA los traduce."""

from enum import StrEnum


class Categoria(StrEnum):
    PLAYA = "PLAYA"
    NATURALEZA = "NATURALEZA"
    CULTURA = "CULTURA"
    GASTRONOMIA = "GASTRONOMIA"
    AVENTURA = "AVENTURA"
    ALOJAMIENTO = "ALOJAMIENTO"


class NivelAlerta(StrEnum):
    INFORMATIVA = "INFORMATIVA"
    PREVENTIVA = "PREVENTIVA"
    CRITICA = "CRITICA"


class ResultadoAuditoria(StrEnum):
    """`resultado` de `auditoria.registrada.v1`."""

    EXITO = "EXITO"
    DENEGADO = "DENEGADO"
    ERROR = "ERROR"


class EstadoReserva(StrEnum):
    """Estados de la reserva según booking-service (Plan §6.4)."""

    SOLICITADA = "SOLICITADA"
    CONFIRMADA = "CONFIRMADA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"

    @property
    def activa(self) -> bool:
        """Una reserva activa ocupa capacidad de carga."""
        return self in (EstadoReserva.SOLICITADA, EstadoReserva.CONFIRMADA)
