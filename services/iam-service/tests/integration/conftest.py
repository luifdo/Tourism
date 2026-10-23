import asyncio
from collections.abc import AsyncIterator

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker

from app.config import get_settings
from app.infrastructure.persistence.database import build_engine


@pytest.fixture
async def connection() -> AsyncIterator[AsyncConnection]:
    """Conexión dentro de una transacción que se deshace al terminar cada prueba.

    Así no quedan filas: la bitácora no admite DELETE y su FK con RESTRICT impide borrar
    los usuarios que referencia. Si PostgreSQL no responde, la prueba se omite.
    """
    engine = build_engine(get_settings().database_url)
    try:
        conn = await asyncio.wait_for(engine.connect(), timeout=3)
    except (SQLAlchemyError, OSError, TimeoutError) as exc:
        await engine.dispose()
        pytest.skip(f"PostgreSQL no responde: {type(exc).__name__}")

    transaction = await conn.begin()
    try:
        yield conn
    finally:
        await transaction.rollback()
        await conn.close()
        await engine.dispose()


@pytest.fixture
def session_factory(connection: AsyncConnection) -> async_sessionmaker[AsyncSession]:
    # El commit() de cada sesión libera un SAVEPOINT; la transacción externa sigue abierta.
    return async_sessionmaker(
        bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
    )
