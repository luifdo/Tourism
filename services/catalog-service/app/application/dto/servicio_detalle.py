from dataclasses import dataclass

from app.application.dto.alerta_vista import AlertaVista
from app.application.dto.prestador_publico import PrestadorPublico
from app.application.dto.servicio_resumen import ServicioResumen
from app.domain.value_objects.texto_traducido import TextoTraducido


@dataclass(frozen=True, slots=True)
class ServicioDetalle:
    """Ficha completa de un servicio activo, con las alertas vigentes del servicio y su zona."""

    resumen: ServicioResumen
    descripcion: TextoTraducido
    capacidad_aforo_diario: int
    imagenes_urls: tuple[str, ...]
    prestador: PrestadorPublico
    alertas: tuple[AlertaVista, ...]
