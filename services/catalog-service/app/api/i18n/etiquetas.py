"""Etiquetas en español e inglés de los valores fijos del sistema.

La API devuelve el código estable (`NATURALEZA`) y su etiqueta en el idioma pedido, para que
la PWA, el chatbot y cualquier otro cliente muestren el mismo texto.
"""

from enum import StrEnum

from app.domain.value_objects.catalogos import Categoria, NivelAlerta
from app.domain.value_objects.idioma import Idioma
from app.domain.value_objects.saturacion import NivelSaturacion

ETIQUETAS: dict[StrEnum, dict[Idioma, str]] = {
    Categoria.PLAYA: {Idioma.ES: "Playa", Idioma.EN: "Beach"},
    Categoria.NATURALEZA: {Idioma.ES: "Naturaleza", Idioma.EN: "Nature"},
    Categoria.CULTURA: {Idioma.ES: "Cultura", Idioma.EN: "Culture"},
    Categoria.GASTRONOMIA: {Idioma.ES: "Gastronomía", Idioma.EN: "Food & dining"},
    Categoria.AVENTURA: {Idioma.ES: "Aventura", Idioma.EN: "Adventure"},
    Categoria.ALOJAMIENTO: {Idioma.ES: "Alojamiento", Idioma.EN: "Lodging"},
    NivelAlerta.INFORMATIVA: {Idioma.ES: "Informativa", Idioma.EN: "Informational"},
    NivelAlerta.PREVENTIVA: {Idioma.ES: "Preventiva", Idioma.EN: "Advisory"},
    NivelAlerta.CRITICA: {Idioma.ES: "Crítica", Idioma.EN: "Critical"},
    NivelSaturacion.BAJO: {Idioma.ES: "Bajo", Idioma.EN: "Low"},
    NivelSaturacion.MEDIO: {Idioma.ES: "Medio", Idioma.EN: "Medium"},
    NivelSaturacion.ALTO: {Idioma.ES: "Alto", Idioma.EN: "High"},
}


def etiqueta(valor: StrEnum, idioma: Idioma) -> str:
    return ETIQUETAS[valor][idioma]
