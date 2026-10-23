"""Condiciones SQL de FiltrosServicio, compartidas por la búsqueda y el mapa.

Los filtros de atributos son una sola contención `atributos @> filtro` sobre el índice GIN
`jsonb_path_ops` (migración 0004). La tabla de servicios debe llamarse `s` en la consulta.
"""

import json
from typing import Any

from app.application.dto.filtros_servicio import FiltrosServicio


def agregar_filtros(
    filtros: FiltrosServicio, condiciones: list[str], parametros: dict[str, Any]
) -> None:
    if filtros.tipos:
        condiciones.append("s.tipo = ANY(:tipos)")
        parametros["tipos"] = [t.value for t in filtros.tipos]
    if filtros.unidad_tarifa:
        condiciones.append("s.unidad_tarifa = :unidad_tarifa")
        parametros["unidad_tarifa"] = filtros.unidad_tarifa.value
    if (filtro := filtros.filtro_atributos()) is not None:
        condiciones.append("s.atributos @> CAST(:atributos AS jsonb)")
        parametros["atributos"] = json.dumps(filtro)
