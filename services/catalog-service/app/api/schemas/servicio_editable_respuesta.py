from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.api.i18n.etiquetas import etiqueta
from app.api.schemas.coordenada_respuesta import CoordenadaRespuesta
from app.api.schemas.texto_traducido_datos import TextoTraducidoDatos
from app.api.schemas.zona_resumen_respuesta import ZonaResumenRespuesta
from app.application.dto.servicio_editable import ServicioEditable
from app.domain.value_objects.catalogos import Categoria
from app.domain.value_objects.idioma import Idioma


class ServicioEditableRespuesta(BaseModel):
    """El servicio con ambos idiomas, para el formulario de edición del prestador."""

    id: UUID
    prestador_id: UUID
    nombre: TextoTraducidoDatos
    descripcion: TextoTraducidoDatos
    categoria: Categoria
    categoria_etiqueta: str
    ubicacion: CoordenadaRespuesta
    tarifa_base: float
    capacidad_aforo_diario: int
    imagenes_urls: list[str]
    zona: ZonaResumenRespuesta | None
    activo: bool
    version: int
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def desde(cls, editable: ServicioEditable, idioma: Idioma) -> "ServicioEditableRespuesta":
        s, d = editable.servicio, editable.servicio.datos
        return cls(
            id=s.id,
            prestador_id=s.prestador_id,
            nombre=TextoTraducidoDatos.desde(d.nombre),
            descripcion=TextoTraducidoDatos.desde(d.descripcion),
            categoria=d.categoria,
            categoria_etiqueta=etiqueta(d.categoria, idioma),
            ubicacion=CoordenadaRespuesta.desde(d.ubicacion),
            tarifa_base=float(d.tarifa_base.valor),
            capacidad_aforo_diario=d.capacidad_aforo_diario,
            imagenes_urls=list(d.imagenes_urls),
            zona=ZonaResumenRespuesta.desde(editable.zona, idioma),
            activo=s.activo,
            version=s.version,
            creado_en=s.creado_en,
            actualizado_en=s.actualizado_en,
        )
