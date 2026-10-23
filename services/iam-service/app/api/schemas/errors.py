from pydantic import BaseModel


class ErrorCampo(BaseModel):
    campo: str
    mensaje: str


class ErrorResponse(BaseModel):
    detail: str
    code: str
    # Solo en los 422 de validación de la petición (code "VALIDACION").
    errores: list[ErrorCampo] | None = None
