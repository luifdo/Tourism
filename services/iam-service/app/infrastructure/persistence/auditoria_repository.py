import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.enums import ResultadoAuditoria
from app.infrastructure.persistence.models import BitacoraAuditoria


class SqlAlchemyAuditoriaRepository:
    """Implementa AuditoriaRepository sobre bitacora_auditoria (solo INSERT)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def registrar(
        self,
        accion: str,
        resultado: ResultadoAuditoria,
        usuario_id: uuid.UUID | None,
        ip_origen: str | None,
        detalles: dict[str, Any],
    ) -> None:
        self._session.add(
            BitacoraAuditoria(
                accion=accion,
                resultado=resultado,
                usuario_id=usuario_id,
                ip_origen=ip_origen,
                detalles=detalles,
            )
        )
        await self._session.flush()
