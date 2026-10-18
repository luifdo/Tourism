from typing import Protocol

from app.application.dto.zona_vista import ZonaVista


class ConsultaZonas(Protocol):
    async def activas(self) -> list[ZonaVista]: ...
