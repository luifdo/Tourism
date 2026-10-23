import uuid

from app.domain.exceptions import TokenInvalidoError
from app.domain.ports.revocacion_tokens import RevocacionTokens
from app.domain.ports.token_service import TokenService
from app.domain.ports.unit_of_work import UnitOfWork
from app.domain.value_objects.enums import ResultadoAuditoria


class CerrarSesion:
    """UC2: cierre de sesión. Revoca el token por su jti hasta que expire."""

    def __init__(self, uow: UnitOfWork, tokens: TokenService, revocacion: RevocacionTokens) -> None:
        self._uow = uow
        self._tokens = tokens
        self._revocacion = revocacion

    async def execute(self, token: str, ip_origen: str | None) -> None:
        claims = self._tokens.verificar(token)
        if await self._revocacion.esta_revocado(claims.jti):
            raise TokenInvalidoError()
        try:
            usuario_id = uuid.UUID(claims.sub)
        except ValueError as exc:
            raise TokenInvalidoError() from exc

        # Primero se revoca: si la bitácora fallara, el token ya no sirve (lo seguro).
        await self._revocacion.revocar(claims.jti, claims.exp)
        async with self._uow as uow:
            await uow.auditoria.registrar(
                accion="LOGOUT",
                resultado=ResultadoAuditoria.EXITO,
                usuario_id=usuario_id,
                ip_origen=ip_origen,
                detalles={},
            )
            await uow.commit()
