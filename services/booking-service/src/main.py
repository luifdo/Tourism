"""Composición del booking-service: conecta cada puerto con su adaptador y crea la app FastAPI.

Ejecución local (desde services/booking-service):
    uvicorn main:app --app-dir src --port 8003 --reload
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI

from application.base import Contexto
from config import Configuracion
from infrastructure.http import demo, operacion, rutas
from infrastructure.http.errores import registrar_manejadores
from infrastructure.messaging.memoria import PublicadorMemoria
from infrastructure.persistence.idempotencia_memoria import AlmacenIdempotenciaMemoria
from infrastructure.persistence.memoria import AlmacenMemoria, fabrica_memoria
from infrastructure.reloj import RelojSistema


@dataclass
class Contenedor:
    ctx: Contexto
    idempotencia: Any
    publicador: Any
    extras: dict[str, Any] = field(default_factory=dict)


def contenedor_memoria(config: Configuracion, reloj: Any = None) -> Contenedor:
    publicador = PublicadorMemoria()
    ctx = Contexto(
        fabrica_memoria(AlmacenMemoria()), publicador, reloj or RelojSistema(), config.plazo_respuesta_horas
    )
    return Contenedor(ctx, AlmacenIdempotenciaMemoria(), publicador)


def crear_app(config: Configuracion | None = None, contenedor: Contenedor | None = None) -> FastAPI:
    config = config or Configuracion()
    if contenedor is None:
        if config.modo_persistencia != "memoria":
            raise NotImplementedError("Solo existe el modo memoria; Postgres y RabbitMQ llegan en el Sprint 5.")
        contenedor = contenedor_memoria(config)
    con_demo = config.modo_persistencia == "memoria" and config.datos_demo

    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI):
        if con_demo:
            await demo.cargar_datos_demo(contenedor)
        yield

    app = FastAPI(
        title="booking-service — Reservas & Cupos (Módulo 3)",
        version="0.1.0",
        description=demo.DESCRIPCION if con_demo else "Contrato: contracts/openapi/booking.yaml",
        lifespan=ciclo_de_vida,
    )
    app.state.contenedor = contenedor
    registrar_manejadores(app)
    operacion.registrar_metricas(app)
    app.include_router(rutas.router)
    app.include_router(operacion.router)
    if con_demo:
        app.include_router(demo.router)
    return app


app = crear_app()
