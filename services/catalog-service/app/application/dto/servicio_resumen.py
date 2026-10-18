from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.application.dto.zona_resumen import ZonaResumen
from app.domain.value_objects.catalogos import Categoria
from app.domain.value_objects.geo import Coordenada
from app.domain.value_objects.texto_traducido import TextoTraducido


@dataclass(frozen=True, slots=True)
class ServicioResumen:
    """Servicio tal como aparece en listados y resultados de búsqueda.

    Los textos van en ambos idiomas; el adaptador HTTP elige el pedido por el usuario.
    """

    id: UUID
    nombre: TextoTraducido
    categoria: Categoria
    ubicacion: Coordenada
    tarifa_base: Decimal
    zona: ZonaResumen | None
    calificacion_promedio: float | None
    total_resenas: int
    imagen_principal: str | None
    distancia_m: int | None = None
