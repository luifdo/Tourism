from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from valkey.asyncio import Valkey

from app.api.errores.manejador_errores import registrar_manejadores
from app.api.middleware.correlacion_middleware import CorrelacionMiddleware
from app.api.routers import alertas, busqueda, health, servicios, zonas
from app.config import Settings, get_settings
from app.infrastructure.cache.consulta_servicios_en_cache import ConsultaServiciosEnCache
from app.infrastructure.observabilidad.configurar_logs import configurar_logs
from app.infrastructure.persistence.consultas.sql_consulta_alertas import SqlConsultaAlertas
from app.infrastructure.persistence.consultas.sql_consulta_servicios import SqlConsultaServicios
from app.infrastructure.persistence.consultas.sql_consulta_zonas import SqlConsultaZonas
from app.infrastructure.persistence.database import build_engine, build_session_factory
from app.infrastructure.reloj import RelojSistema


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configurar_logs(settings.service_name, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = build_engine(settings.database_url)
        sesiones = build_session_factory(engine)
        # Tiempos cortos: si Valkey se cae, la búsqueda sigue sin caché casi sin demora.
        valkey = Valkey.from_url(
            settings.valkey_url,
            socket_timeout=settings.valkey_timeout_seconds,
            socket_connect_timeout=settings.valkey_timeout_seconds,
        )
        app.state.engine = engine
        app.state.reloj = RelojSistema()
        app.state.consulta_servicios = ConsultaServiciosEnCache(
            SqlConsultaServicios(sesiones), valkey
        )
        app.state.consulta_zonas = SqlConsultaZonas(sesiones)
        app.state.consulta_alertas = SqlConsultaAlertas(sesiones)
        yield
        await valkey.aclose()
        await engine.dispose()

    app = FastAPI(title=settings.service_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(CorrelacionMiddleware)
    registrar_manejadores(app)
    for modulo in (health, servicios, busqueda, zonas, alertas):
        app.include_router(modulo.router)
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    return app


app = create_app()
