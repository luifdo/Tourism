import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from app.application.use_cases.cerrar_sesion import CerrarSesion
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import ServicioNoDisponibleError, TokenInvalidoError
from app.domain.value_objects.enums import ResultadoAuditoria, Rol
from app.infrastructure.cache.valkey_revocacion import ValkeyRevocacionTokens
from tests.conftest import LlavesRsa, crear_token_service
from tests.fakes import FakeUnitOfWork

AHORA = datetime.now(UTC).replace(microsecond=0)
USUARIO = Usuario(
    id=uuid.uuid4(),
    email="maria.perez@example.com",
    password_hash="x",
    nombre_completo="María Pérez",
    rol=Rol.TURISTA,
    habeas_data_aceptado=True,
    habeas_data_aceptado_en=AHORA,
)


class FakeRedisClient:
    """Lo mínimo de redis.asyncio.Redis que usa ValkeyRevocacionTokens."""

    def __init__(self, caido: bool = False) -> None:
        self.ttls: dict[str, int] = {}
        self.caido = caido

    async def set(self, key: str, value: Any, ex: int) -> None:
        if self.caido:
            raise RedisConnectionError("Valkey caído")
        self.ttls[key] = ex

    async def exists(self, key: str) -> int:
        if self.caido:
            raise RedisConnectionError("Valkey caído")
        return int(key in self.ttls)


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


def cerrar(
    llaves: LlavesRsa, uow: FakeUnitOfWork, redis: FakeRedisClient, segundos_despues: int = 60
) -> CerrarSesion:
    # La revocación ocurre `segundos_despues` de emitido el token.
    revocacion = ValkeyRevocacionTokens(
        redis,  # type: ignore[arg-type]
        reloj=lambda: AHORA + timedelta(seconds=segundos_despues),
    )
    return CerrarSesion(uow=uow, tokens=crear_token_service(llaves), revocacion=revocacion)


def token(llaves: LlavesRsa) -> tuple[str, str]:
    emitido = crear_token_service(llaves, reloj=AHORA).emitir(USUARIO)
    return emitido.access_token, emitido.jti


async def test_revoca_con_el_ttl_restante(llaves_rsa: LlavesRsa, uow: FakeUnitOfWork) -> None:
    redis = FakeRedisClient()
    access_token, jti = token(llaves_rsa)

    await cerrar(llaves_rsa, uow, redis, segundos_despues=60).execute(access_token, "190.0.0.1")

    # 15 min de vida - 60 s transcurridos = 840 s.
    assert redis.ttls == {f"iam:revoked:{jti}": 840}
    assert uow.commits == 1
    [registro] = uow.auditoria.registros
    assert (registro.accion, registro.resultado) == ("LOGOUT", ResultadoAuditoria.EXITO)
    assert registro.usuario_id == USUARIO.id
    assert registro.ip_origen == "190.0.0.1"


async def test_ttl_minimo_de_un_segundo(llaves_rsa: LlavesRsa) -> None:
    redis = FakeRedisClient()
    revocacion = ValkeyRevocacionTokens(redis, reloj=lambda: AHORA)  # type: ignore[arg-type]

    await revocacion.revocar("jti-ya-vencido", expira_en=AHORA - timedelta(seconds=30))

    assert redis.ttls == {"iam:revoked:jti-ya-vencido": 1}


async def test_token_ya_revocado(llaves_rsa: LlavesRsa, uow: FakeUnitOfWork) -> None:
    redis = FakeRedisClient()
    access_token, _ = token(llaves_rsa)
    caso = cerrar(llaves_rsa, uow, redis)
    await caso.execute(access_token, None)

    with pytest.raises(TokenInvalidoError):
        await caso.execute(access_token, None)

    assert [r.accion for r in uow.auditoria.registros] == ["LOGOUT"]


async def test_token_invalido(llaves_rsa: LlavesRsa, uow: FakeUnitOfWork) -> None:
    redis = FakeRedisClient()

    with pytest.raises(TokenInvalidoError):
        await cerrar(llaves_rsa, uow, redis).execute("no-es-un-token", None)

    assert redis.ttls == {}
    assert uow.auditoria.registros == []


async def test_valkey_caido_falla_cerrado(llaves_rsa: LlavesRsa, uow: FakeUnitOfWork) -> None:
    access_token, _ = token(llaves_rsa)

    with pytest.raises(ServicioNoDisponibleError):
        await cerrar(llaves_rsa, uow, FakeRedisClient(caido=True)).execute(access_token, None)

    assert uow.auditoria.registros == []
