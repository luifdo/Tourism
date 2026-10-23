"""Etiquetas en español e inglés de los valores fijos del sistema.

La API devuelve el código estable (`NATURALEZA`) y su etiqueta en el idioma pedido, para que
la PWA, el chatbot y cualquier otro cliente muestren el mismo texto.
"""

from enum import StrEnum

from app.domain.value_objects.catalogos import Categoria, NivelAlerta, UnidadTarifa
from app.domain.value_objects.idioma import Idioma
from app.domain.value_objects.saturacion import NivelSaturacion
from app.domain.value_objects.tipo_servicio import TipoServicio

_ES, _EN = Idioma.ES, Idioma.EN
_T = TipoServicio
_U = UnidadTarifa

ETIQUETAS: dict[StrEnum, dict[Idioma, str]] = {
    Categoria.PLAYA: {Idioma.ES: "Playa", Idioma.EN: "Beach"},
    Categoria.NATURALEZA: {Idioma.ES: "Naturaleza", Idioma.EN: "Nature"},
    Categoria.CULTURA: {Idioma.ES: "Cultura", Idioma.EN: "Culture"},
    Categoria.GASTRONOMIA: {Idioma.ES: "Gastronomía", Idioma.EN: "Food & dining"},
    Categoria.AVENTURA: {Idioma.ES: "Aventura", Idioma.EN: "Adventure"},
    Categoria.ALOJAMIENTO: {Idioma.ES: "Alojamiento", Idioma.EN: "Lodging"},
    Categoria.TRANSPORTE: {Idioma.ES: "Transporte", Idioma.EN: "Transport"},
    _T.HOTEL: {_ES: "Hotel", _EN: "Hotel"},
    _T.HOSTAL: {_ES: "Hostal", _EN: "Hostel"},
    _T.POSADA_ECOHOTEL: {_ES: "Posada o ecohotel", _EN: "Guesthouse or eco-lodge"},
    _T.GLAMPING_CAMPING: {_ES: "Glamping o camping", _EN: "Glamping or camping"},
    _T.APARTAMENTO_TURISTICO: {_ES: "Apartamento turístico", _EN: "Holiday apartment"},
    _T.RESTAURANTE: {_ES: "Restaurante", _EN: "Restaurant"},
    _T.CAFE_BAR: {_ES: "Café o bar", _EN: "Café or bar"},
    _T.EXPERIENCIA_GASTRONOMICA: {_ES: "Experiencia gastronómica", _EN: "Food experience"},
    _T.TOUR_GUIADO: {_ES: "Tour guiado", _EN: "Guided tour"},
    _T.SENDERISMO: {_ES: "Senderismo", _EN: "Hiking"},
    _T.DEPORTE_ACUATICO: {_ES: "Deporte acuático", _EN: "Water sport"},
    _T.AVISTAMIENTO: {_ES: "Avistamiento de aves y fauna", _EN: "Bird and wildlife watching"},
    _T.RESERVA_PARQUE: {_ES: "Reserva o parque", _EN: "Reserve or park"},
    _T.ACCESO_PLAYA: {_ES: "Acceso a playa", _EN: "Beach access"},
    _T.ALQUILER_EQUIPO: {_ES: "Alquiler de equipo", _EN: "Equipment rental"},
    _T.TOUR_CULTURAL: {_ES: "Tour histórico o cultural", _EN: "Historical or cultural tour"},
    _T.MUSEO_SITIO: {_ES: "Museo o sitio", _EN: "Museum or site"},
    _T.EXPERIENCIA_COMUNITARIA: {_ES: "Experiencia comunitaria", _EN: "Community experience"},
    _T.EVENTO_FESTIVAL: {_ES: "Evento o festival", _EN: "Event or festival"},
    _T.TRANSPORTE_MARITIMO: {_ES: "Transporte en lancha", _EN: "Boat transport"},
    _T.TRASLADO_TERRESTRE: {_ES: "Traslado terrestre", _EN: "Ground transfer"},
    _U.POR_PERSONA: {_ES: "por persona", _EN: "per person"},
    _U.POR_NOCHE: {_ES: "por noche", _EN: "per night"},
    _U.POR_GRUPO: {_ES: "por grupo", _EN: "per group"},
    _U.POR_UNIDAD: {_ES: "por unidad", _EN: "per unit"},
    _U.POR_HORA: {_ES: "por hora", _EN: "per hour"},
    _U.POR_DIA: {_ES: "por día", _EN: "per day"},
    NivelAlerta.INFORMATIVA: {Idioma.ES: "Informativa", Idioma.EN: "Informational"},
    NivelAlerta.PREVENTIVA: {Idioma.ES: "Preventiva", Idioma.EN: "Advisory"},
    NivelAlerta.CRITICA: {Idioma.ES: "Crítica", Idioma.EN: "Critical"},
    NivelSaturacion.BAJO: {Idioma.ES: "Bajo", Idioma.EN: "Low"},
    NivelSaturacion.MEDIO: {Idioma.ES: "Medio", Idioma.EN: "Medium"},
    NivelSaturacion.ALTO: {Idioma.ES: "Alto", Idioma.EN: "High"},
}


def etiqueta(valor: StrEnum, idioma: Idioma) -> str:
    return ETIQUETAS[valor][idioma]
