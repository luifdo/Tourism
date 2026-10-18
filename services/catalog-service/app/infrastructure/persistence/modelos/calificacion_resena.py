"""Modelo ORM de la tabla `calificacion_resena` (esquema en la migración 0001)."""

from uuid import UUID

from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database import Base


class CalificacionResenaModelo(Base):
    __tablename__ = "calificacion_resena"

    resena_id: Mapped[UUID] = mapped_column(primary_key=True)
    servicio_id: Mapped[UUID]
    puntuacion: Mapped[int] = mapped_column(SmallInteger)
