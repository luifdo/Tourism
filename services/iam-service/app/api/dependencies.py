from collections.abc import Callable
from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.use_cases.check_health import CheckHealth
from app.application.use_cases.registrar_usuario import RegistrarUsuario
from app.config import Settings, get_settings
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.unit_of_work import UnitOfWork
from app.infrastructure.persistence.database import SqlAlchemyDatabaseProbe
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher


def get_engine(request: Request) -> AsyncEngine:
    return request.app.state.engine


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory


def get_check_health(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CheckHealth:
    probe = SqlAlchemyDatabaseProbe(engine, settings.database_health_timeout_seconds)
    return CheckHealth(database=probe)


def get_unit_of_work(
    session_factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory)


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()


def get_reloj() -> Callable[[], datetime]:
    return lambda: datetime.now(UTC)


def get_registrar_usuario(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    reloj: Annotated[Callable[[], datetime], Depends(get_reloj)],
) -> RegistrarUsuario:
    return RegistrarUsuario(uow=uow, hasher=hasher, reloj=reloj)
