"""Dobles en memoria de los puertos, para probar sin base de datos."""

import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from types import TracebackType
from typing import Any, Self

from app.domain.entities.usuario import Usuario
from app.domain.exceptions import UsuarioYaExisteError
from app.domain.value_objects.email import Email
from app.domain.value_objects.enums import ResultadoAuditoria

AHORA = datetime(2026, 10, 23, 15, 0, tzinfo=UTC)


def reloj_fijo() -> datetime:
    return AHORA


class FakeUsuarioRepository:
    def __init__(self) -> None:
        self.por_email: dict[str, Usuario] = {}

    async def add(self, usuario: Usuario) -> Usuario:
        if usuario.email in self.por_email:
            raise UsuarioYaExisteError()
        guardado = replace(usuario, id=uuid.uuid4(), creado_en=AHORA, actualizado_en=AHORA)
        self.por_email[usuario.email] = guardado
        return guardado

    async def find_by_email(self, email: Email) -> Usuario | None:
        return self.por_email.get(email.value)


@dataclass
class RegistroAuditoria:
    accion: str
    resultado: ResultadoAuditoria
    usuario_id: uuid.UUID | None
    ip_origen: str | None
    detalles: dict[str, Any]


class FakeAuditoriaRepository:
    def __init__(self) -> None:
        self.registros: list[RegistroAuditoria] = []

    async def registrar(
        self,
        accion: str,
        resultado: ResultadoAuditoria,
        usuario_id: uuid.UUID | None,
        ip_origen: str | None,
        detalles: dict[str, Any],
    ) -> None:
        self.registros.append(RegistroAuditoria(accion, resultado, usuario_id, ip_origen, detalles))


class FakeUnitOfWork:
    """Cuenta commits y rollbacks. Los repositorios persisten entre usos, como una base real."""

    def __init__(self) -> None:
        self.usuarios = FakeUsuarioRepository()
        self.auditoria = FakeAuditoriaRepository()
        self.commits = 0
        self.rollbacks = 0
        self._committed = False

    async def __aenter__(self) -> Self:
        self._committed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if not self._committed:
            await self.rollback()

    async def commit(self) -> None:
        self.commits += 1
        self._committed = True

    async def rollback(self) -> None:
        self.rollbacks += 1
