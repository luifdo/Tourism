"""Caché de búsqueda en Valkey como decorador de ConsultaServicios (Plan §6.2, ESC-02).

* Clave: `catalog:buscar:{generación}:{idioma}:{hash de los criterios}`, TTL de 300 s.
* Invalidación: cada cambio del catálogo incrementa `catalog:buscar:gen`; las claves de la
  generación anterior quedan huérfanas y expiran solas (no hace falta SCAN ni borrar).
* Si Valkey falla o tarda, se consulta PostGIS directamente: la caché nunca tumba la búsqueda.
* El detalle de un servicio no se cachea: lleva alertas vigentes que deben verse al instante.
"""

import hashlib
import logging
from datetime import datetime
from uuid import UUID

from pydantic import TypeAdapter
from valkey.asyncio import Valkey
from valkey.exceptions import ValkeyError

from app.application.dto.criterios_busqueda import CriteriosBusqueda
from app.application.dto.pagina_servicios import PaginaServicios
from app.application.dto.servicio_detalle import ServicioDetalle
from app.application.ports.consulta_servicios import ConsultaServicios

logger = logging.getLogger(__name__)

CLAVE_GENERACION = "catalog:buscar:gen"
TTL_SEGUNDOS = 300

_criterios_json = TypeAdapter(CriteriosBusqueda)
_pagina_json = TypeAdapter(PaginaServicios)
_FALLAS = (ValkeyError, OSError, TimeoutError)


class ConsultaServiciosEnCache:
    def __init__(self, origen: ConsultaServicios, valkey: Valkey) -> None:
        self._origen = origen
        self._valkey = valkey

    async def buscar(self, criterios: CriteriosBusqueda) -> PaginaServicios:
        clave = await self._clave(criterios)
        if clave is not None:
            guardado = await self._leer(clave)
            if guardado is not None:
                return guardado
        pagina = await self._origen.buscar(criterios)
        if clave is not None:
            await self._escribir(clave, pagina)
        return pagina

    async def detalle(self, servicio_id: UUID, ahora: datetime) -> ServicioDetalle | None:
        return await self._origen.detalle(servicio_id, ahora)

    async def invalidar(self) -> None:
        """Se llama después de confirmar un cambio del catálogo (servicio, zona, perfil)."""
        try:
            await self._valkey.incr(CLAVE_GENERACION)
        except _FALLAS:
            logger.warning("No se pudo invalidar la caché de búsqueda", exc_info=True)

    async def _clave(self, criterios: CriteriosBusqueda) -> str | None:
        try:
            generacion = int(await self._valkey.get(CLAVE_GENERACION) or 0)
        except _FALLAS:
            logger.warning("Valkey no responde; búsqueda sin caché", exc_info=True)
            return None
        huella = hashlib.sha256(_criterios_json.dump_json(criterios)).hexdigest()[:32]
        return f"catalog:buscar:{generacion}:{criterios.idioma.value}:{huella}"

    async def _leer(self, clave: str) -> PaginaServicios | None:
        try:
            valor = await self._valkey.get(clave)
        except _FALLAS:
            logger.warning("Valkey no responde; búsqueda sin caché", exc_info=True)
            return None
        return _pagina_json.validate_json(valor) if valor is not None else None

    async def _escribir(self, clave: str, pagina: PaginaServicios) -> None:
        try:
            await self._valkey.set(clave, _pagina_json.dump_json(pagina), ex=TTL_SEGUNDOS)
        except _FALLAS:
            logger.warning("No se pudo guardar en la caché de búsqueda", exc_info=True)
