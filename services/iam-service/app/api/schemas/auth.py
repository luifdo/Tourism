import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.value_objects.enums import Rol


class RegistroRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "maria.perez@example.com",
                    "password": "Tayrona2026",
                    "nombre_completo": "María Pérez",
                    "rol": "Turista",
                    "habeas_data_aceptado": True,
                    "es_mayor_de_edad": True,
                }
            ]
        }
    )

    email: EmailStr
    password: str
    nombre_completo: str
    rol: Literal["Turista", "Prestador"]
    habeas_data_aceptado: bool
    es_mayor_de_edad: bool


class UsuarioPublicoResponse(BaseModel):
    """Datos públicos de una cuenta. Nunca incluye la contraseña ni su hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    nombre_completo: str
    rol: Rol
    email_verificado: bool
    creado_en: datetime
