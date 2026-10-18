"""Modelo ORM de la tabla `prestador_perfil` (esquema en la migración 0001)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database import Base


class PrestadorPerfilModelo(Base):
    __tablename__ = "prestador_perfil"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(unique=True)
    razon_social: Mapped[str | None] = mapped_column(Text)
    telefono: Mapped[str | None] = mapped_column(Text)
    direccion: Mapped[str | None] = mapped_column(Text)
    politica_cancelacion: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    activo: Mapped[bool]
    version: Mapped[int]
    creado_en: Mapped[datetime] = mapped_column(server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(server_default=func.now())
