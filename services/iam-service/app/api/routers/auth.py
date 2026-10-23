import ipaddress
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_registrar_usuario
from app.api.schemas.auth import RegistroRequest, UsuarioPublicoResponse
from app.api.schemas.errors import ErrorResponse
from app.application.use_cases.registrar_usuario import RegistrarUsuario, RegistrarUsuarioCommand
from app.domain.value_objects.enums import Rol

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
