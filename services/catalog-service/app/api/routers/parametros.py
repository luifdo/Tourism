"""Conversión de parámetros de consulta compartida por los routers de lectura."""

from app.domain.errors import DatoInvalido
from app.domain.value_objects.catalogos import Categoria
from app.domain.value_objects.geo import Bbox, Coordenada


def bbox(valor: str) -> Bbox:
    """Vista del mapa como `minLon,minLat,maxLon,maxLat` (el formato de Leaflet `toBBoxString`)."""
    partes = valor.split(",")
    if len(partes) != 4:
        raise DatoInvalido(campo="bbox", regla="cuatro_valores")
    try:
        numeros = [float(p) for p in partes]
    except ValueError as exc:
        raise DatoInvalido(campo="bbox", regla="numero") from exc
    return Bbox.desde_lista(numeros)


def bbox_opcional(valor: str | None) -> Bbox | None:
    return bbox(valor) if valor is not None else None


def coordenada_opcional(lat: float | None, lon: float | None) -> Coordenada | None:
    """`lat` y `lon` van juntos o no van."""
    if lat is None and lon is None:
        return None
    if lat is None or lon is None:
        faltante = "lat" if lat is None else "lon"
        raise DatoInvalido(campo=faltante, regla="obligatorio")
    return Coordenada(lat=lat, lon=lon)


def categorias(valor: str | None) -> tuple[Categoria, ...]:
    """Lista separada por comas (`PLAYA,CULTURA`), como define el contrato."""
    if not valor:
        return ()
    try:
        return tuple(Categoria(c.strip().upper()) for c in valor.split(",") if c.strip())
    except ValueError as exc:
        raise DatoInvalido(campo="categoria", regla="formato") from exc
