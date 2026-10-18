"""Utilidades compartidas por los repositorios SQLAlchemy de escritura.

* `obtener` bloquea la fila (`SELECT ... FOR UPDATE`): con varias réplicas, dos ediciones
  simultáneas del mismo registro se ordenan y la segunda ve la versión nueva (409), en vez
  de pisar la primera.
* `guardar` es un upsert por llave primaria; las columnas generadas no se escriben.
"""

from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.texto_traducido import TextoTraducido


def texto_o_none(valor: dict[str, str] | None) -> TextoTraducido | None:
    return TextoTraducido(**valor) if valor else None


async def upsert(session: AsyncSession, modelo: Any, valores: dict[str, Any]) -> None:
    llaves = [c.name for c in modelo.__table__.primary_key.columns]
    sentencia = insert(modelo).values(**valores)
    actualizar = {k: sentencia.excluded[k] for k in valores if k not in llaves}
    await session.execute(sentencia.on_conflict_do_update(index_elements=llaves, set_=actualizar))
