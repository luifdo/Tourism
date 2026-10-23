import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

pytestmark = pytest.mark.integration


async def test_zonas_iniciales_bilingues(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        filas = (
            await conn.execute(text("SELECT codigo, nombre FROM zona WHERE activa ORDER BY codigo"))
        ).all()
    codigos = [codigo for codigo, _ in filas]
    assert codigos == [
        "bahia-concha",
        "centro-historico",
        "el-rodadero",
        "minca",
        "parque-tayrona",
        "taganga",
    ]
    assert all(set(nombre) == {"es", "en"} for _, nombre in filas)


async def test_zonas_iniciales_no_se_superponen(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        cruces = await conn.scalar(
            text(
                "SELECT count(*) FROM zona a JOIN zona b"
                " ON a.id < b.id AND ST_Intersects(a.poligono, b.poligono)"
            )
        )
    assert cruces == 0


def test_bajar_y_subir_migraciones(alembic_cfg: Config) -> None:
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")


async def test_tipo_unidad_y_atributos_son_obligatorios(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        columnas = dict(
            (
                await conn.execute(
                    text(
                        "SELECT column_name, is_nullable FROM information_schema.columns"
                        " WHERE table_name = 'atractivo_servicio'"
                        " AND column_name IN ('tipo', 'unidad_tarifa', 'atributos')"
                    )
                )
            ).all()
        )
        indices = set(
            await conn.scalars(
                text("SELECT indexname FROM pg_indexes WHERE tablename = 'atractivo_servicio'")
            )
        )
    assert columnas == {"tipo": "NO", "unidad_tarifa": "NO", "atributos": "NO"}
    assert {"ix_servicio_tipo", "ix_servicio_atributos"} <= indices
