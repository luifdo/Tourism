import asyncio
import uuid
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta

import pytest
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import get_settings
from app.infrastructure.cache.valkey_revocacion import (
    PREFIJO,
    ValkeyRevocacionTokens,
    build_valkey_client,
)

pytestmark = pytest.mark.valkey


@pytest.fixture
async def valkey() -> AsyncIterator[Redis]:
    client = build_valkey_client(get_settings().valkey_url)
    try:
        await asyncio.wait_for(client.ping(), timeout=3)
    except (RedisError, OSError, TimeoutError) as exc:
        await client.aclose()
        pytest.skip(f"Valkey no responde: {type(exc).__name__}")
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
async def nuevo_jti(valkey: Redis) -> AsyncIterator[Callable[[], str]]:
    """Genera jti de prueba y borra sus llaves al terminar."""
    creados: list[str] = []

    def crear() -> str:
        creados.append(f"prueba-{uuid.uuid4()}")
        return creados[-1]

    yield crear
    if creados:
        await valkey.delete(*(PREFIJO + jti for jti in creados))


@pytest.fixture
def revocacion(valkey: Redis) -> ValkeyRevocacionTokens:
    return ValkeyRevocacionTokens(valkey, reloj=lambda: datetime.now(UTC))


async def test_revocar_y_consultar(
    revocacion: ValkeyRevocacionTokens, nuevo_jti: Callable[[], str]
) -> None:
    jti = nuevo_jti()

    assert await revocacion.esta_revocado(jti) is False
    await revocacion.revocar(jti, expira_en=datetime.now(UTC) + timedelta(seconds=120))

    assert await revocacion.esta_revocado(jti) is True
    assert await revocacion.esta_revocado(nuevo_jti()) is False


async def test_ttl_cercano_al_tiempo_restante_del_token(
    valkey: Redis, revocacion: ValkeyRevocacionTokens, nuevo_jti: Callable[[], str]
) -> None:
    jti = nuevo_jti()

    await revocacion.revocar(jti, expira_en=datetime.now(UTC) + timedelta(seconds=120))

    ttl = await valkey.ttl(PREFIJO + jti)
    assert 115 <= ttl <= 120
