from app.api.schemas.alerta_respuesta import AlertaRespuesta
from app.api.schemas.prestador_publico_respuesta import PrestadorPublicoRespuesta
from app.api.schemas.servicio_resumen_respuesta import ServicioResumenRespuesta
from app.application.dto.servicio_detalle import ServicioDetalle
from app.domain.value_objects.idioma import Idioma


class ServicioDetalleRespuesta(ServicioResumenRespuesta):
    descripcion: str
    capacidad_aforo_diario: int
    imagenes_urls: list[str]
    prestador: PrestadorPublicoRespuesta
    alertas: list[AlertaRespuesta]

    @classmethod
    def desde(cls, detalle: ServicioDetalle, idioma: Idioma) -> "ServicioDetalleRespuesta":  # type: ignore[override]
        resumen = ServicioResumenRespuesta.desde(detalle.resumen, idioma)
        return cls(
            **resumen.model_dump(),
            descripcion=detalle.descripcion.en_idioma(idioma)[0],
            capacidad_aforo_diario=detalle.capacidad_aforo_diario,
            imagenes_urls=list(detalle.imagenes_urls),
            prestador=PrestadorPublicoRespuesta.desde(detalle.prestador, idioma),
            alertas=[AlertaRespuesta.desde(a, idioma) for a in detalle.alertas],
        )
