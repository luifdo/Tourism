"""Traduce errores a respuestas HTTP con el formato común y en el idioma de la petición."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.i18n.mensajes_error import mensaje_codigo, mensaje_error, mensaje_validacion
from app.api.schemas.error_respuesta import ErrorRespuesta
from app.domain.errors import ErrorDominio, VersionDistinta
from app.domain.value_objects.idioma import Idioma
from app.infrastructure.observabilidad.contexto_correlacion import correlation_id_actual

logger = logging.getLogger(__name__)

ESTADO_POR_CODIGO = {
    "VALIDACION": status.HTTP_400_BAD_REQUEST,
    "NO_ENCONTRADO": status.HTTP_404_NOT_FOUND,
    "ROL_NO_PERMITIDO": status.HTTP_403_FORBIDDEN,
    "PERFIL_INACTIVO": status.HTTP_403_FORBIDDEN,
    "VERSION_DISTINTA": status.HTTP_409_CONFLICT,
    "ZONA_EN_USO": status.HTTP_409_CONFLICT,
    "CODIGO_EXISTENTE": status.HTTP_409_CONFLICT,
    "FALTA_IF_MATCH": status.HTTP_428_PRECONDITION_REQUIRED,
}

# Tipos de error de Pydantic que corresponden a un dato faltante.
_FALTANTES = {"missing", "missing_argument"}


def _respuesta(
    estado: int, codigo: str, mensaje: str, idioma: Idioma, cabeceras: dict[str, str] | None = None
) -> JSONResponse:
    cuerpo = ErrorRespuesta(error=codigo, message=mensaje, correlation_id=correlation_id_actual())
    return JSONResponse(
        cuerpo.model_dump(),
        status_code=estado,
        headers={"Content-Language": idioma.value, **(cabeceras or {})},
    )


def _idioma(request: Request) -> Idioma:
    return Idioma.desde_accept_language(request.headers.get("accept-language"))


async def manejar_error_dominio(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ErrorDominio)
    idioma = _idioma(request)
    cabeceras = {"ETag": f'"{exc.version_actual}"'} if isinstance(exc, VersionDistinta) else None
    estado = ESTADO_POR_CODIGO.get(exc.codigo, status.HTTP_400_BAD_REQUEST)
    return _respuesta(estado, exc.codigo, mensaje_error(exc, idioma), idioma, cabeceras)


async def manejar_validacion(request: Request, exc: Exception) -> JSONResponse:
    """Parámetros que no cumplen el esquema (tipos, rangos, faltantes) → VALIDACION 400."""
    assert isinstance(exc, RequestValidationError)
    idioma = _idioma(request)
    primero = exc.errors()[0] if exc.errors() else {}
    campo = str(primero.get("loc", ["?"])[-1])
    regla = "obligatorio" if primero.get("type") in _FALTANTES else "formato"
    return _respuesta(
        status.HTTP_400_BAD_REQUEST,
        "VALIDACION",
        mensaje_validacion(regla, idioma, {"campo": campo}),
        idioma,
    )


async def manejar_inesperado(request: Request, exc: Exception) -> JSONResponse:
    # Este manejador corre fuera de los middlewares: la cabecera de correlación va aquí.
    logger.exception("Error inesperado atendiendo %s %s", request.method, request.url.path)
    idioma = _idioma(request)
    return _respuesta(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "ERROR_INTERNO",
        mensaje_codigo("ERROR_INTERNO", idioma),
        idioma,
        {"X-Correlation-ID": correlation_id_actual() or ""},
    )


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorDominio, manejar_error_dominio)
    app.add_exception_handler(RequestValidationError, manejar_validacion)
    app.add_exception_handler(Exception, manejar_inesperado)
