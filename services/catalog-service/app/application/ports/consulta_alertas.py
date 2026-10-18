from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.application.dto.alerta_vista import AlertaVista


class ConsultaAlertas(Protocol):
    async def vigentes(
        self, ahora: datetime, zona: str | None = None, servicio_id: UUID | None = None
    ) -> list[AlertaVista]:
        """Alertas activas y no expiradas, de mayor a menor nivel.

        Con `servicio_id` incluye también las alertas de la zona del servicio, porque afectan
        a quien lo visita.
        """
        ...
