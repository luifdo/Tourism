"""Lectura de zonas activas (implementa ConsultaZonas)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.dto.zona_vista import ZonaVista
from app.domain.value_objects.geo import Coordenada
from app.domain.value_objects.texto_traducido import TextoTraducido

# ST_PointOnSurface garantiza un punto dentro del polígono (el centroide puede caer fuera).
# Se redondea a 6 decimales (~10 cm) para no exponer ruido de punto flotante.
_ACTIVAS = """
    SELECT id, codigo, nombre,
           round(ST_Y(ST_PointOnSurface(poligono))::numeric, 6)::float8 AS lat,
           round(ST_X(ST_PointOnSurface(poligono))::numeric, 6)::float8 AS lon
    FROM zona
    WHERE activa
    ORDER BY codigo
"""


class SqlConsultaZonas:
    def __init__(self, sesiones: async_sessionmaker[AsyncSession]) -> None:
        self._sesiones = sesiones

    async def activas(self) -> list[ZonaVista]:
        async with self._sesiones() as session:
            filas = (await session.execute(text(_ACTIVAS))).all()
        return [
            ZonaVista(
                id=f.id,
                codigo=f.codigo,
                nombre=TextoTraducido(**f.nombre),
                centro=Coordenada(lat=f.lat, lon=f.lon),
            )
            for f in filas
        ]
