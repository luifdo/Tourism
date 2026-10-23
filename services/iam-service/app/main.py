from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.errors import register_error_handlers
from app.api.routers import auth, health
from app.config import Settings, get_settings
from app.infrastructure.persistence.database import build_engine, build_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.engine = build_engine(settings.database_url)
        app.state.session_factory = build_session_factory(app.state.engine)
        yield
        await app.state.engine.dispose()

    app = FastAPI(title=settings.service_name, version="0.1.0", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    return app


app = create_app()
