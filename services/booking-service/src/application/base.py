"""Dependencias comunes de los casos de uso."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.ports import FabricaUnidadDeTrabajo, PublicadorEventos, Reloj
from domain.reglas import PLAZO_RESPUESTA_HORAS
from domain.reserva import EventoDominio, Reserva


@dataclass
class Contexto:
    uow: FabricaUnidadDeTrabajo
    publicador: PublicadorEventos
    reloj: Reloj
    plazo_horas: int = PLAZO_RESPUESTA_HORAS


def evento_auditoria(usuario_id: UUID | None, accion: str, **detalles: Any) -> EventoDominio:
    """auditoria.registrada: el Módulo 1 lo guarda en la bitácora (Plan §4.4)."""
    return EventoDominio(
        "auditoria.registrada",
        {
            "usuario_id": str(usuario_id) if usuario_id else None,
            "accion": accion,
            "resultado": "EXITO",
            "detalles": {k: str(v) for k, v in detalles.items()},
        },
    )


def eventos_de(reserva: Reserva, usuario_id: UUID | None) -> list[EventoDominio]:
    """Eventos de la reserva más su registro de auditoría."""
    eventos = reserva.extraer_eventos()
    auditoria = [
        evento_auditoria(
            usuario_id,
            "RESERVA_" + e.tipo.split(".")[1].upper(),
            reserva_id=reserva.id,
        )
        for e in eventos
    ]
    return eventos + auditoria
