"""Cableado de casos de uso con sus adaptadores.

Los adaptadores (engine, sesiones, Valkey, consultas) se crean una vez en el lifespan de
`main.py` y viven en `app.state`; aquí solo se arman los casos de uso por petición. Las
pruebas reemplazan estas funciones con `app.dependency_overrides`.
"""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine

from app.application.ports.consulta_alertas import ConsultaAlertas
from app.application.ports.consulta_mapa import ConsultaMapa
from app.application.ports.consulta_servicios import ConsultaServicios
from app.application.ports.consulta_zonas import ConsultaZonas
from app.application.use_cases.buscar_servicios import BuscarServicios
from app.application.use_cases.check_health import CheckHealth
from app.application.use_cases.listar_alertas import ListarAlertas
from app.application.use_cases.listar_zonas import ListarZonas
from app.application.use_cases.obtener_servicio import ObtenerServicio
from app.application.use_cases.ver_alertas_en_mapa import VerAlertasEnMapa
from app.application.use_cases.ver_servicios_en_mapa import VerServiciosEnMapa
from app.application.use_cases.ver_zonas_en_mapa import VerZonasEnMapa
from app.config import Settings, get_settings
from app.domain.ports.reloj import Reloj
from app.infrastructure.persistence.database import SqlAlchemyDatabaseProbe


def get_engine(request: Request) -> AsyncEngine:
    return request.app.state.engine


def get_reloj(request: Request) -> Reloj:
    return request.app.state.reloj


def get_consulta_servicios(request: Request) -> ConsultaServicios:
    return request.app.state.consulta_servicios


def get_consulta_zonas(request: Request) -> ConsultaZonas:
    return request.app.state.consulta_zonas


def get_consulta_alertas(request: Request) -> ConsultaAlertas:
    return request.app.state.consulta_alertas


def get_consulta_mapa(request: Request) -> ConsultaMapa:
    return request.app.state.consulta_mapa


def get_check_health(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CheckHealth:
    probe = SqlAlchemyDatabaseProbe(engine, settings.database_health_timeout_seconds)
    return CheckHealth(database=probe)


def get_buscar_servicios(
    consulta: Annotated[ConsultaServicios, Depends(get_consulta_servicios)],
) -> BuscarServicios:
    return BuscarServicios(consulta)


def get_obtener_servicio(
    consulta: Annotated[ConsultaServicios, Depends(get_consulta_servicios)],
    reloj: Annotated[Reloj, Depends(get_reloj)],
) -> ObtenerServicio:
    return ObtenerServicio(consulta, reloj)


def get_listar_zonas(
    consulta: Annotated[ConsultaZonas, Depends(get_consulta_zonas)],
) -> ListarZonas:
    return ListarZonas(consulta)


def get_listar_alertas(
    consulta: Annotated[ConsultaAlertas, Depends(get_consulta_alertas)],
    reloj: Annotated[Reloj, Depends(get_reloj)],
) -> ListarAlertas:
    return ListarAlertas(consulta, reloj)


def get_ver_servicios_en_mapa(
    consulta: Annotated[ConsultaMapa, Depends(get_consulta_mapa)],
) -> VerServiciosEnMapa:
    return VerServiciosEnMapa(consulta)


def get_ver_zonas_en_mapa(
    consulta: Annotated[ConsultaMapa, Depends(get_consulta_mapa)],
) -> VerZonasEnMapa:
    return VerZonasEnMapa(consulta)


def get_ver_alertas_en_mapa(
    consulta: Annotated[ConsultaMapa, Depends(get_consulta_mapa)],
    reloj: Annotated[Reloj, Depends(get_reloj)],
) -> VerAlertasEnMapa:
    return VerAlertasEnMapa(consulta, reloj)
