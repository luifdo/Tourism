import uuid
from typing import Any, Protocol

from app.domain.value_objects.enums import ResultadoAuditoria


class AuditoriaRepository(Protocol):
    """Bitácora de auditoría de solo inserción (RNF-10)."""

    async def registrar(
        self,
        accion: str,
        resultado: ResultadoAuditoria,
        usuario_id: uuid.UUID | None,
        ip_origen: str | None,
        detalles: dict[str, Any],
    ) -> None: ...
