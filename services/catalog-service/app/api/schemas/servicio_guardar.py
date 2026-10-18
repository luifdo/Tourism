from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.coordenada_respuesta import CoordenadaRespuesta
from app.api.schemas.texto_traducido_datos import TextoTraducidoDatos
from app.domain.entities.atractivo_servicio import MAX_IMAGENES, DatosServicio
from app.domain.value_objects.catalogos import Categoria
from app.domain.value_objects.geo import Coordenada
from app.domain.value_objects.tarifa import Tarifa


class ServicioGuardar(BaseModel):
    """Cuerpo de UC17 (registrar) y UC18 (editar). Las reglas finas las valida el dominio."""

    model_config = ConfigDict(extra="forbid")

    nombre: TextoTraducidoDatos
    descripcion: TextoTraducidoDatos
    categoria: Categoria
    ubicacion: CoordenadaRespuesta
    tarifa_base: Decimal = Field(ge=0)
    capacidad_aforo_diario: int = Field(ge=1)
    imagenes_urls: list[str] = Field(default_factory=list, max_length=MAX_IMAGENES)

    def a_dominio(self) -> DatosServicio:
        return DatosServicio(
            nombre=self.nombre.a_dominio(),
            descripcion=self.descripcion.a_dominio(),
            categoria=self.categoria,
            ubicacion=Coordenada(lat=self.ubicacion.lat, lon=self.ubicacion.lon),
            tarifa_base=Tarifa(self.tarifa_base),
            capacidad_aforo_diario=self.capacidad_aforo_diario,
            imagenes_urls=tuple(self.imagenes_urls),
        )
