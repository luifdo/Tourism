"""PostGIS real y efímero (testcontainers) con las migraciones aplicadas.

Requiere Docker. Si no está disponible, las pruebas de integración se omiten.
"""

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.config import get_settings
from app.infrastructure.persistence.database import build_engine, build_session_factory

RAIZ = Path(__file__).resolve().parents[2]
IMAGEN = "postgis/postgis:16-3.4"
TABLAS_DE_PRUEBA = (
    "outbox",
    "evento_procesado",
    "calificacion_resena",
    "reserva_proyeccion",
    "alerta_oficial",
    "atractivo_servicio",
    "prestador_perfil",
)


def alembic_config() -> Config:
    config = Config(str(RAIZ / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ / "migrations"))
    return config


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    try:
        from testcontainers.community.postgres import PostgresContainer

        contenedor = PostgresContainer(IMAGEN, driver="asyncpg").start()
    except Exception as exc:  # Docker apagado o no instalado
        pytest.skip(f"Docker no disponible para las pruebas de integración: {exc}")
    url = contenedor.get_connection_url()
    anterior = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    get_settings.cache_clear()
    command.upgrade(alembic_config(), "head")
    yield url
    contenedor.stop()
    if anterior is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = anterior
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def valkey_url() -> Iterator[str]:
    try:
        from testcontainers.community.valkey import ValkeyContainer

        contenedor = ValkeyContainer("valkey/valkey:8").start()
    except Exception as exc:
        pytest.skip(f"Docker no disponible: {exc}")
    yield contenedor.get_connection_url()
    contenedor.stop()


@pytest.fixture(scope="session")
def rabbitmq_url() -> Iterator[str]:
    try:
        from testcontainers.community.rabbitmq import RabbitMqContainer

        contenedor = RabbitMqContainer("rabbitmq:4-management").start()
    except Exception as exc:
        pytest.skip(f"Docker no disponible: {exc}")
    host = contenedor.get_container_host_ip()
    yield f"amqp://guest:guest@{host}:{contenedor.get_exposed_port(5672)}/"
    contenedor.stop()


@pytest.fixture
def alembic_cfg(database_url: str) -> Config:
    return alembic_config()


@pytest.fixture
async def engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    engine = build_engine(database_url)
    yield engine
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {', '.join(TABLAS_DE_PRUEBA)} CASCADE"))
        await conn.execute(text("DELETE FROM zona WHERE codigo LIKE 'prueba-%'"))
    await engine.dispose()


@pytest.fixture
def sesiones(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return build_session_factory(engine)
