from app.api.schemas.pagina_servicios_respuesta import PaginaServiciosRespuesta
from app.application.dto.pagina_servicios import PaginaServicios
from app.domain.value_objects.idioma import Idioma


class ResultadoBusquedaRespuesta(PaginaServiciosRespuesta):
    # Nulo mientras la búsqueda no filtre por `fecha` (integración con booking, paso 14).
    disponibilidad_verificada: bool | None = None

    @classmethod
    def desde(cls, pagina: PaginaServicios, idioma: Idioma) -> "ResultadoBusquedaRespuesta":
        base = PaginaServiciosRespuesta.desde(pagina, idioma)
        return cls(**base.model_dump())
