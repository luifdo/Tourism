from dataclasses import replace

import pytest

from app.application.use_cases.iniciar_sesion import (
    HASH_RELLENO,
    IniciarSesion,
    IniciarSesionCommand,
)
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import CredencialesInvalidasError, CuentaInactivaError
from app.domain.value_objects.enums import ResultadoAuditoria, Rol
from app.infrastructure.security.jwt_token_service import JwtTokenService
from tests.fakes import AHORA, FakePasswordHasher, FakeUnitOfWork

PASSWORD = "Tayrona2026"
COMANDO = IniciarSesionCommand(
    email="  Maria.Perez@Example.com ", password=PASSWORD, ip_origen="190.0.0.1"
)


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


def sembrar(uow: FakeUnitOfWork, hasher: FakePasswordHasher, activo: bool = True) -> Usuario:
    return uow.usuarios.sembrar(
        Usuario(
            email="maria.perez@example.com",
            password_hash=hasher.hash(PASSWORD),
            nombre_completo="María Pérez",
            rol=Rol.TURISTA,
            activo=activo,
            email_verificado=False,
            habeas_data_aceptado=True,
            habeas_data_aceptado_en=AHORA,
        )
    )


def iniciar(
    uow: FakeUnitOfWork, hasher: FakePasswordHasher, token_service: JwtTokenService
) -> IniciarSesion:
    return IniciarSesion(uow=uow, hasher=hasher, tokens=token_service)


async def test_login_exitoso(
    uow: FakeUnitOfWork, hasher: FakePasswordHasher, token_service: JwtTokenService
) -> None:
    existente = sembrar(uow, hasher)

    token, usuario = await iniciar(uow, hasher, token_service).execute(COMANDO)

    assert usuario.id == existente.id
    assert usuario.email_verificado is False  # no bloquea el login por ahora
    claims = token_service.verificar(token.access_token)
    assert claims.sub == str(existente.id)
    assert claims.rol is Rol.TURISTA
    assert uow.commits == 1
    [registro] = uow.auditoria.registros
    assert (registro.accion, registro.resultado) == ("LOGIN_SUCCESS", ResultadoAuditoria.EXITO)
    assert registro.usuario_id == existente.id
    assert registro.ip_origen == "190.0.0.1"
    # Sin rehash: el hash guardado no cambia.
    assert uow.usuarios.por_email[existente.email].password_hash == existente.password_hash


async def test_password_incorrecta(
    uow: FakeUnitOfWork, hasher: FakePasswordHasher, token_service: JwtTokenService
) -> None:
    existente = sembrar(uow, hasher)

    with pytest.raises(CredencialesInvalidasError):
        await iniciar(uow, hasher, token_service).execute(replace(COMANDO, password="otra123"))

    assert uow.commits == 1  # el fallo queda confirmado en la bitácora
    [registro] = uow.auditoria.registros
    assert (registro.accion, registro.resultado) == ("LOGIN_FAIL", ResultadoAuditoria.DENEGADO)
    assert registro.usuario_id == existente.id
    assert registro.detalles == {"motivo": "password_incorrecta"}


@pytest.mark.parametrize("email", ["nadie@example.com", "no-es-un-email"])
async def test_usuario_inexistente_verifica_contra_el_hash_de_relleno(
    uow: FakeUnitOfWork, hasher: FakePasswordHasher, token_service: JwtTokenService, email: str
) -> None:
    sembrar(uow, hasher)

    with pytest.raises(CredencialesInvalidasError):
        await iniciar(uow, hasher, token_service).execute(replace(COMANDO, email=email))

    assert hasher.verificados == [HASH_RELLENO]
    assert uow.commits == 1
    [registro] = uow.auditoria.registros
    assert (registro.accion, registro.resultado) == ("LOGIN_FAIL", ResultadoAuditoria.DENEGADO)
    assert registro.usuario_id is None
    assert registro.detalles == {"motivo": "usuario_no_existe"}  # sin el correo intentado


async def test_cuenta_inactiva(
    uow: FakeUnitOfWork, hasher: FakePasswordHasher, token_service: JwtTokenService
) -> None:
    existente = sembrar(uow, hasher, activo=False)

    with pytest.raises(CuentaInactivaError):
        await iniciar(uow, hasher, token_service).execute(COMANDO)

    assert uow.commits == 1
    [registro] = uow.auditoria.registros
    assert (registro.accion, registro.resultado) == ("LOGIN_FAIL", ResultadoAuditoria.DENEGADO)
    assert registro.usuario_id == existente.id
    assert registro.detalles == {"motivo": "cuenta_inactiva"}


async def test_cuenta_inactiva_con_password_incorrecta_no_revela_el_estado(
    uow: FakeUnitOfWork, hasher: FakePasswordHasher, token_service: JwtTokenService
) -> None:
    sembrar(uow, hasher, activo=False)

    with pytest.raises(CredencialesInvalidasError):
        await iniciar(uow, hasher, token_service).execute(replace(COMANDO, password="otra123"))

    assert uow.auditoria.registros[0].detalles == {"motivo": "password_incorrecta"}


async def test_rehash_cuando_los_parametros_cambiaron(
    uow: FakeUnitOfWork, token_service: JwtTokenService
) -> None:
    existente = sembrar(uow, FakePasswordHasher(version=1))
    hasher_actual = FakePasswordHasher(version=2)

    await iniciar(uow, hasher_actual, token_service).execute(COMANDO)

    guardado = uow.usuarios.por_email[existente.email].password_hash
    assert guardado != existente.password_hash
    assert guardado == hasher_actual.hash(PASSWORD)
    assert uow.commits == 1  # rehash y LOGIN_SUCCESS en la misma transacción
    assert [r.accion for r in uow.auditoria.registros] == ["LOGIN_SUCCESS"]


async def test_sin_rehash_si_los_parametros_no_cambiaron(
    uow: FakeUnitOfWork, hasher: FakePasswordHasher, token_service: JwtTokenService
) -> None:
    existente = sembrar(uow, hasher)

    await iniciar(uow, hasher, token_service).execute(COMANDO)

    assert uow.usuarios.por_email[existente.email].password_hash == existente.password_hash
