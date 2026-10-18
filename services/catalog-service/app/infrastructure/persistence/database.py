import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base declarativa de los modelos ORM; Alembic la usa para autogenerar migraciones."""


def build_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True)


class SqlAlchemyDatabaseProbe:
    """Implementa DatabaseProbe ejecutando SELECT 1 contra PostgreSQL."""

    def __init__(self, engine: AsyncEngine, timeout_seconds: float) -> None:
        self._engine = engine
        self._timeout_seconds = timeout_seconds

    async def ping(self) -> bool:
        try:
            async with asyncio.timeout(self._timeout_seconds):
                async with self._engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
        except (SQLAlchemyError, OSError, TimeoutError):
            logger.warning("La base de datos no responde", exc_info=True)
            return False
        return True
