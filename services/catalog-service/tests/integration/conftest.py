"""PostGIS, Valkey y RabbitMQ reales y efímeros (testcontainers), con las migraciones aplicadas.

Requiere Docker. Si no está disponible, las pruebas de integración se omiten.
"""

import asyncio
import json
import os
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from pathlib import Path
from typing import Any
from uuid import uuid4

import aio_pika
import pytest
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from valkey.asyncio import Valkey

from app.application.dto.resultado_consumo import ResultadoConsumo
from app.config import get_settings
from app.infrastructure.messaging.consumidor_rabbitmq import ConsumidorRabbitMQ
from app.infrastructure.messaging.esquemas.sobre_evento import SobreEvento
from app.infrastructure.messaging.topologia_rabbitmq import EXCHANGE_DLX, declarar_topologia
from app.infrastructure.persistence.database import build_engine, build_session_factory

RAIZ = Path(__file__).resolve().parents[2]
IMAGEN = "postgis/postgis:16-3.4"
EXCHANGE = "turismo.eventos"
# Esperas de reintento cortas: las pruebas no esperan los 1 s / 5 s / 25 s de producción.
ESPERAS = (0.2, 0.2, 0.2)
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


class Bus:
    """Publica como lo haría el servicio productor y escucha la DLQ con una cola propia."""

    def __init__(self, url: str) -> None:
        self.url = url

    async def __aenter__(self) -> "Bus":
        self._conexion = await aio_pika.connect_robust(self.url)
        canal = await self._conexion.channel()
        self._eventos = await declarar_topologia(canal, EXCHANGE)
        dlx = await canal.declare_exchange(EXCHANGE_DLX, aio_pika.ExchangeType.TOPIC, durable=True)
        self.dlq: AbstractQueue = await canal.declare_queue(exclusive=True)
        await self.dlq.bind(dlx, routing_key="#")
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._conexion.close()

    async def publicar(self, cuerpo: dict[str, Any]) -> None:
        await self._eventos.publish(
            aio_pika.Message(json.dumps(cuerpo).encode(), type=cuerpo.get("event_type")),
            routing_key=cuerpo.get("event_type", "prestador.aprobado"),
        )

    async def de_la_dlq(self) -> AbstractIncomingMessage:
        mensaje = await self.dlq.get(timeout=5, fail=False)
        for _ in range(50):
            if mensaje is not None:
                await mensaje.ack()
                return mensaje
            await asyncio.sleep(0.1)
            mensaje = await self.dlq.get(fail=False)
        raise AssertionError("No llegó nada a la DLQ")


@pytest.fixture
async def valkey(valkey_url: str) -> AsyncIterator[Valkey]:
    cliente = Valkey.from_url(valkey_url)
    yield cliente
    await cliente.aclose()


@pytest.fixture
async def bus(rabbitmq_url: str) -> AsyncIterator[Bus]:
    async with Bus(rabbitmq_url) as b:
        yield b


Manejar = Callable[[SobreEvento], Awaitable[ResultadoConsumo]]


@pytest.fixture
async def consumir(
    rabbitmq_url: str,
) -> AsyncIterator[Callable[[tuple[str, ...], Manejar], Awaitable[None]]]:
    """Arranca un consumidor en una cola propia (nombre único) con las claves dadas."""
    consumidores: list[ConsumidorRabbitMQ] = []

    async def iniciar(claves: tuple[str, ...], manejar: Manejar) -> None:
        consumidor = ConsumidorRabbitMQ(
            rabbitmq_url, EXCHANGE, f"prueba.{uuid4().hex[:8]}", claves, manejar, ESPERAS
        )
        await consumidor.iniciar()
        consumidores.append(consumidor)

    yield iniciar
    for consumidor in consumidores:
        await consumidor.cerrar()
