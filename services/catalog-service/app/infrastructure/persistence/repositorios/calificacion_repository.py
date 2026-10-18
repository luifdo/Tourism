"""Repositorio de CalificacionResena (tabla `calificacion_resena`)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.calificacion_resena import CalificacionResena
from app.infrastructure.persistence.modelos.calificacion_resena import CalificacionResenaModelo
from app.infrastructure.persistence.repositorios.comun import upsert


class SqlCalificacionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def guardar(self, calificacion: CalificacionResena) -> None:
        await upsert(
            self._session,
            CalificacionResenaModelo,
            {
                "resena_id": calificacion.resena_id,
                "servicio_id": calificacion.servicio_id,
                "puntuacion": calificacion.puntuacion,
            },
        )
