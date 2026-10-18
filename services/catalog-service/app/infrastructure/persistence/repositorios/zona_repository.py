"""Repositorio de Zona (tabla `zona`) y asignación de zonas con PostGIS."""

import json
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.zona import Zona
from app.domain.value_objects.codigo_zona import CodigoZona
from app.domain.value_objects.geo import Coordenada, PoligonoGeoJSON
from app.domain.value_objects.texto_traducido import TextoTraducido
from app.infrastructure.persistence.modelos.zona import ZonaModelo

# Zona activa que cubre un punto; si varias lo cubren, gana la de menor área (la más específica).
_ZONA_QUE_CUBRE = """
    SELECT z.id FROM zona z
    WHERE z.activa AND ST_Covers(z.poligono, {punto})
    ORDER BY ST_Area(z.poligono) ASC
    LIMIT 1
"""


class SqlZonaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def obtener(self, zona_id: UUID) -> Zona | None:
        return await self._uno(ZonaModelo.id == zona_id)

    async def obtener_por_codigo(self, codigo: CodigoZona) -> Zona | None:
        return await self._uno(ZonaModelo.codigo == codigo.valor)

    async def zona_de(self, punto: Coordenada) -> UUID | None:
        consulta = _ZONA_QUE_CUBRE.format(punto="ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)")
        return await self._session.scalar(text(consulta), {"lon": punto.lon, "lat": punto.lat})

    async def reasignar_servicios(self, zona_id: UUID) -> None:
        """Recalcula la zona de los servicios que estaban en ella o que su polígono cubre ahora."""
        consulta = _ZONA_QUE_CUBRE.format(punto="s.ubicacion::geometry")
        await self._session.execute(
            text(
                f"""
                UPDATE atractivo_servicio s
                SET zona_id = ({consulta})
                WHERE s.zona_id = :zona_id
                   OR ST_Covers((SELECT poligono FROM zona WHERE id = :zona_id),
                                s.ubicacion::geometry)
                """
            ),
            {"zona_id": zona_id},
        )

    async def guardar(self, zona: Zona) -> None:
        sentencia = insert(ZonaModelo).values(
            id=zona.id,
            codigo=zona.codigo.valor,
            nombre=zona.nombre.a_dict(),
            poligono=func.ST_Multi(
                func.ST_SetSRID(
                    func.ST_GeomFromGeoJSON(json.dumps(zona.poligono.a_geojson())), 4326
                )
            ),
            activa=zona.activa,
            version=zona.version,
        )
        columnas = ("codigo", "nombre", "poligono", "activa", "version")
        await self._session.execute(
            sentencia.on_conflict_do_update(
                index_elements=["id"], set_={c: sentencia.excluded[c] for c in columnas}
            )
        )

    async def _uno(self, condicion: Any) -> Zona | None:
        resultado = await self._session.execute(
            select(ZonaModelo, func.ST_AsGeoJSON(ZonaModelo.poligono, 15))
            .where(condicion)
            .with_for_update()
        )
        fila = resultado.first()
        if fila is None:
            return None
        modelo, geojson = fila
        return Zona(
            id=modelo.id,
            codigo=CodigoZona(modelo.codigo),
            nombre=TextoTraducido(**modelo.nombre),
            poligono=PoligonoGeoJSON.desde_geojson(json.loads(geojson)),
            activa=modelo.activa,
            version=modelo.version,
        )
