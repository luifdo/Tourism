"""Modelos ORM de catalog_db. Reflejan la migración 0001; el esquema lo manda Alembic.

Son detalles de infraestructura: los repositorios los traducen a entidades del dominio y
el dominio nunca los importa.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from geoalchemy2 import Geography, Geometry
from sqlalchemy import Computed, Numeric, SmallInteger, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
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


class ZonaModelo(Base):
    __tablename__ = "zona"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(Text, unique=True)
    nombre: Mapped[dict[str, str]] = mapped_column(JSONB)
    poligono: Mapped[Any] = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326, spatial_index=False)
    )
    activa: Mapped[bool]
    version: Mapped[int]


class AtractivoServicioModelo(Base):
    __tablename__ = "atractivo_servicio"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    prestador_id: Mapped[UUID]
    prestador_usuario_id: Mapped[UUID]
    nombre: Mapped[dict[str, str]] = mapped_column(JSONB)
    descripcion: Mapped[dict[str, str]] = mapped_column(JSONB)
    categoria: Mapped[str] = mapped_column(Text)
    lat: Mapped[float]
    lon: Mapped[float]
    ubicacion: Mapped[Any] = mapped_column(
        Geography("POINT", srid=4326, spatial_index=False),
        Computed("ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography", persisted=True),
    )
    tarifa_base: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    capacidad_aforo_diario: Mapped[int]
    imagenes_urls: Mapped[list[str]] = mapped_column(ARRAY(Text))
    zona_id: Mapped[UUID | None]
    activo: Mapped[bool]
    desactivado_por_suspension: Mapped[bool]
    version: Mapped[int]
    creado_en: Mapped[datetime]
    actualizado_en: Mapped[datetime]
    busqueda_es: Mapped[Any] = mapped_column(TSVECTOR, Computed("busqueda_es", persisted=True))
    busqueda_en: Mapped[Any] = mapped_column(TSVECTOR, Computed("busqueda_en", persisted=True))


class AlertaOficialModelo(Base):
    __tablename__ = "alerta_oficial"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    nivel: Mapped[str] = mapped_column(Text)
    mensaje: Mapped[dict[str, str]] = mapped_column(JSONB)
    entidad_usuario_id: Mapped[UUID]
    servicio_id: Mapped[UUID | None]
    zona_id: Mapped[UUID | None]
    fecha_expiracion: Mapped[datetime]
    creada_en: Mapped[datetime]
    activa: Mapped[bool]


class ReservaProyeccionModelo(Base):
    __tablename__ = "reserva_proyeccion"

    reserva_id: Mapped[UUID] = mapped_column(primary_key=True)
    servicio_id: Mapped[UUID]
    prestador_id: Mapped[UUID]
    turista_id: Mapped[UUID]
    fecha_reserva: Mapped[date]
    numero_personas: Mapped[int]
    estado: Mapped[str] = mapped_column(Text)
    ultimo_evento_en: Mapped[datetime]


class CalificacionResenaModelo(Base):
    __tablename__ = "calificacion_resena"

    resena_id: Mapped[UUID] = mapped_column(primary_key=True)
    servicio_id: Mapped[UUID]
    puntuacion: Mapped[int] = mapped_column(SmallInteger)


class EventoProcesadoModelo(Base):
    __tablename__ = "evento_procesado"

    event_id: Mapped[UUID] = mapped_column(primary_key=True)
    consumidor: Mapped[str] = mapped_column(Text, primary_key=True)


class OutboxModelo(Base):
    __tablename__ = "outbox"

    event_id: Mapped[UUID] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(Text)
    sobre: Mapped[dict[str, Any]] = mapped_column(JSONB)
    creado_en: Mapped[datetime]
    publicado_en: Mapped[datetime | None]
    intentos: Mapped[int]
