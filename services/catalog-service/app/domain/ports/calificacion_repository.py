"""Puerto de persistencia `CalificacionRepository` (adaptador en persistence/repositorios)."""

from typing import Protocol

from app.domain.entities.calificacion_resena import CalificacionResena


class CalificacionRepository(Protocol):
    async def guardar(self, calificacion: CalificacionResena) -> None:
        """Inserta o actualiza por `resena_id`."""
        ...
