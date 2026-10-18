from uuid import UUID

from pydantic import BaseModel

from app.api.i18n.etiquetas import etiqueta
from app.api.schemas.coordenada_respuesta import CoordenadaRespuesta
from app.api.schemas.zona_resumen_respuesta import ZonaResumenRespuesta
from app.application.dto.servicio_resumen import ServicioResumen
from app.domain.value_objects.catalogos import Categoria
from app.domain.value_objects.idioma import Idioma


class ServicioResumenRespuesta(BaseModel):
    id: UUID
    nombre: str
    categoria: Categoria
    categoria_etiqueta: str
    zona: ZonaResumenRespuesta | None
    ubicacion: CoordenadaRespuesta
    tarifa_base: float  # número en JSON (el contrato lo define así); Decimal en el dominio
    calificacion_promedio: float | None
    total_resenas: int
    imagen_principal: str | None
    distancia_m: int | None = None

    @classmethod
    def desde(cls, servicio: ServicioResumen, idioma: Idioma) -> "ServicioResumenRespuesta":
        return cls(
            id=servicio.id,
            nombre=servicio.nombre.en_idioma(idioma)[0],
            categoria=servicio.categoria,
            categoria_etiqueta=etiqueta(servicio.categoria, idioma),
            zona=ZonaResumenRespuesta.desde(servicio.zona, idioma),
            ubicacion=CoordenadaRespuesta.desde(servicio.ubicacion),
            tarifa_base=float(servicio.tarifa_base),
            calificacion_promedio=servicio.calificacion_promedio,
            total_resenas=servicio.total_resenas,
            imagen_principal=servicio.imagen_principal,
            distancia_m=servicio.distancia_m,
        )
