import ipaddress
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import (
    get_cerrar_sesion,
    get_iniciar_sesion,
    get_registrar_usuario,
    get_token_service,
)
from app.api.schemas.auth import (
    JwksResponse,
    LoginRequest,
    LoginResponse,
    RegistroRequest,
    UsuarioPublicoResponse,
)
from app.api.schemas.errors import ErrorResponse
from app.application.use_cases.cerrar_sesion import CerrarSesion
from app.application.use_cases.iniciar_sesion import IniciarSesion, IniciarSesionCommand
from app.application.use_cases.registrar_usuario import RegistrarUsuario, RegistrarUsuarioCommand
from app.domain.exceptions import TokenInvalidoError
from app.domain.value_objects.enums import Rol
from app.infrastructure.security.jwt_token_service import JwtTokenService

router = APIRouter(prefix="/api/iam", tags=["auth"])


def _ip_origen(request: Request) -> str | None:
    # uvicorn --proxy-headers ya pone aquí la IP real si viene de un proxy de confianza.
    host = request.client.host if request.client else None
    try:
        return str(ipaddress.ip_address(host)) if host else None
    except ValueError:
        # Clientes que no reportan una IP (p. ej. "testclient"); la columna es INET.
        return None


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioPublicoResponse,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "El correo ya está registrado (EMAIL_EN_USO).",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": (
                "Petición inválida (VALIDACION, con la lista 'errores') o regla de negocio "
                "incumplida (HABEAS_DATA_REQUERIDO, MAYORIA_DE_EDAD_REQUERIDA, "
                "PASSWORD_INVALIDA, NOMBRE_INVALIDO)."
            ),
        },
    },
)
async def register(
    body: RegistroRequest,
    request: Request,
    registrar: Annotated[RegistrarUsuario, Depends(get_registrar_usuario)],
) -> UsuarioPublicoResponse:
    usuario = await registrar.execute(
        RegistrarUsuarioCommand(
            email=body.email,
            password=body.password,
            nombre_completo=body.nombre_completo,
            rol=Rol(body.rol),
            habeas_data_aceptado=body.habeas_data_aceptado,
            es_mayor_de_edad=body.es_mayor_de_edad,
            ip_origen=_ip_origen(request),
        )
    )
    return UsuarioPublicoResponse.model_validate(usuario)


_ERROR_401 = {
    "model": ErrorResponse,
    "description": "Correo o contraseña incorrectos (CREDENCIALES_INVALIDAS). "
    "Incluye el encabezado WWW-Authenticate: Bearer.",
}


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: _ERROR_401,
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "La cuenta está desactivada (CUENTA_INACTIVA).",
        },
    },
)
async def login(
    body: LoginRequest,
    request: Request,
    iniciar: Annotated[IniciarSesion, Depends(get_iniciar_sesion)],
) -> LoginResponse:
    token, usuario = await iniciar.execute(
        IniciarSesionCommand(
            email=body.email, password=body.password, ip_origen=_ip_origen(request)
        )
    )
    return LoginResponse(
        access_token=token.access_token,
        expires_in=token.expires_in,
        usuario=UsuarioPublicoResponse.model_validate(usuario),
    )


# auto_error=False: sin token respondemos 401 TOKEN_INVALIDO con el formato de error común.
_bearer = HTTPBearer(auto_error=False)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido, expirado o ya revocado (TOKEN_INVALIDO).",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "No se pudo consultar la lista de revocación (SERVICIO_NO_DISPONIBLE).",
        },
    },
)
async def logout(
    request: Request,
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    cerrar: Annotated[CerrarSesion, Depends(get_cerrar_sesion)],
) -> Response:
    if credenciales is None:
        raise TokenInvalidoError()
    await cerrar.execute(credenciales.credentials, _ip_origen(request))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/.well-known/jwks.json", response_model=JwksResponse)
async def jwks(
    response: Response, tokens: Annotated[JwtTokenService, Depends(get_token_service)]
) -> dict[str, Any]:
    """Llaves públicas para que el Gateway y los demás servicios verifiquen los tokens."""
    response.headers["Cache-Control"] = "public, max-age=300"
    return tokens.jwks()
