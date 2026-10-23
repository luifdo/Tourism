"""Analítica del destino: capacidad de carga (UC24) y mapa de calor (RF-07)."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.dependencies import get_consultar_capacidad, get_ver_mapa_calor
from app.api.i18n.idioma_peticion import idioma_peticion
from app.api.respuesta_geojson import RespuestaGeoJSON
from app.api.routers.parametros import bbox_opcional
from app.api.schemas.capacidad_zona_respuesta import CapacidadZonaRespuesta
from app.api.schemas.coleccion_mapa_calor import ColeccionMapaCalor
from app.api.schemas.error_respuesta import ErrorRespuesta
from app.api.seguridad.identidad_peticion import identidad_peticion
from app.application.dto.escala_mapa import ZOOM_MAXIMO, ZOOM_MINIMO, EscalaMapa
from app.application.use_cases.consultar_capacidad import ConsultarCapacidad
from app.application.use_cases.ver_mapa_calor import VerMapaCalor
from app.domain.value_objects.identidad import Identidad, Rol
from app.domain.value_objects.idioma import Idioma

router = APIRouter(prefix="/api/catalog/analitica", tags=["Analítica"])

IdentidadDep = Annotated[Identidad, Depends(identidad_peticion)]
IdiomaDep = Annotated[Idioma, Depends(idioma_peticion)]
_ERRORES = {
    400: {"model": ErrorRespuesta},
    401: {"model": ErrorRespuesta},
    403: {"model": ErrorRespuesta},
}


@router.get(
    "/capacidad",
    summary="Presión sobre la capacidad de carga (UC24)",
    response_model=list[CapacidadZonaRespuesta],
    responses=_ERRORES | {404: {"model": ErrorRespuesta}},
)
async def capacidad(
    identidad: IdentidadDep,
    idioma: IdiomaDep,
    consultar: Annotated[ConsultarCapacidad, Depends(get_consultar_capacidad)],
    zona: Annotated[str | None, Query(pattern=r"^[a-z0-9-]{2,40}$")] = None,
    fecha: date | None = None,
) -> JSONResponse:
    zonas = await consultar.execute(identidad, fecha, zona)
    solo_nivel = identidad.rol is Rol.TURISTA
    cuerpo = [
        CapacidadZonaRespuesta.desde(z, idioma, solo_nivel).model_dump(
            mode="json", exclude_none=True
        )
        for z in zonas
    ]
    return JSONResponse(cuerpo, headers={"Content-Language": idioma.value})


@router.get(
    "/mapa-calor",
    summary="Mapa de calor de saturación por zona (RF-07)",
    response_model=ColeccionMapaCalor,
    response_class=RespuestaGeoJSON,
    responses=_ERRORES,
)
async def mapa_calor(
    identidad: IdentidadDep,
    idioma: IdiomaDep,
    ver: Annotated[VerMapaCalor, Depends(get_ver_mapa_calor)],
    fecha: date | None = None,
    vista: Annotated[str | None, Query(alias="bbox")] = None,
    zoom: Annotated[int, Query(ge=ZOOM_MINIMO, le=ZOOM_MAXIMO)] = 12,
) -> ColeccionMapaCalor:
    zonas = await ver.execute(identidad, fecha, bbox_opcional(vista), EscalaMapa(zoom))
    return ColeccionMapaCalor.desde(zonas, idioma)
