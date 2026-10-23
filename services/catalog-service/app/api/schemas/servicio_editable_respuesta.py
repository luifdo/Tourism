from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.api.i18n.etiquetas import etiqueta
from app.api.schemas.atributos.atributos_servicio_datos import AtributosServicioDatos
from app.api.schemas.coordenada_respuesta import CoordenadaRespuesta
from app.api.schemas.texto_traducido_datos import TextoTraducidoDatos
from app.api.schemas.zona_resumen_respuesta import ZonaResumenRespuesta
from app.application.dto.servicio_editable import ServicioEditable
from app.domain.value_objects.catalogos import Categoria, UnidadTarifa
from app.domain.value_objects.idioma import Idioma
from app.domain.value_objects.tipo_servicio import TipoServicio


class ServicioEditableRespuesta(BaseModel):
    """El servicio con ambos idiomas, para el formulario de edición del prestador."""

    id: UUID
    prestador_id: UUID
    nombre: TextoTraducidoDatos
    descripcion: TextoTraducidoDatos
    tipo: TipoServicio
    tipo_etiqueta: str
    categoria: Categoria
    categoria_etiqueta: str
    ubicacion: CoordenadaRespuesta
    tarifa_base: float
    unidad_tarifa: UnidadTarifa
    unidad_tarifa_etiqueta: str
    capacidad_aforo_diario: int
    imagenes_urls: list[str]
    atributos: AtributosServicioDatos
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
            tipo=d.tipo,
            tipo_etiqueta=etiqueta(d.tipo, idioma),
            categoria=d.categoria,
            categoria_etiqueta=etiqueta(d.categoria, idioma),
            ubicacion=CoordenadaRespuesta.desde(d.ubicacion),
            tarifa_base=float(d.tarifa_base.valor),
            unidad_tarifa=d.unidad_tarifa,
            unidad_tarifa_etiqueta=etiqueta(d.unidad_tarifa, idioma),
            capacidad_aforo_diario=d.capacidad_aforo_diario,
            imagenes_urls=list(d.imagenes_urls),
            atributos=AtributosServicioDatos.desde(d.atributos),
            zona=ZonaResumenRespuesta.desde(editable.zona, idioma),
            activo=s.activo,
            version=s.version,
            creado_en=s.creado_en,
            actualizado_en=s.actualizado_en,
        )
