import re
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Any

from app.domain.errors import DatoInvalido
from app.domain.value_objects.atributos.valores import NivelFisico, OpcionDietaria
from app.domain.value_objects.catalogos import Categoria, UnidadTarifa
from app.domain.value_objects.geo import Coordenada
from app.domain.value_objects.idioma import Idioma
from app.domain.value_objects.tipo_servicio import TipoServicio

RADIO_POR_DEFECTO_M = 5000
RADIO_MAXIMO_M = 50000
_IDIOMA = re.compile(r"^[a-z]{2}$")


class OrdenBusqueda(StrEnum):
    RELEVANCIA = "relevancia"
    DISTANCIA = "distancia"
    PRECIO = "precio"
    CALIFICACION = "calificacion"


@dataclass(frozen=True, slots=True)
class CriteriosBusqueda:
    """Filtros de UC7/UC8 ya validados. Es también la llave de la caché de búsqueda."""

    idioma: Idioma
    pagina: int = 1
    tamano: int = 20
    texto: str | None = None
    categorias: tuple[Categoria, ...] = field(default_factory=tuple)
    zona: str | None = None
    precio_min: Decimal | None = None
    precio_max: Decimal | None = None
    cerca_de: Coordenada | None = None
    radio_m: int = RADIO_POR_DEFECTO_M
    orden: OrdenBusqueda = OrdenBusqueda.CALIFICACION
    tipos: tuple[TipoServicio, ...] = field(default_factory=tuple)
    unidad_tarifa: UnidadTarifa | None = None
    # Filtros sobre `atributos` (JSONB). Un sí/no filtra por lo que el prestador informó:
    # `accesible=False` trae los que dijeron que no, no los que no lo informaron.
    idioma_atencion: str | None = None
    accesible: bool | None = None
    mascotas: bool | None = None
    apto_ninos: bool | None = None
    opcion_dietaria: OpcionDietaria | None = None
    nivel_fisico: NivelFisico | None = None
    acepta_pago_digital: bool | None = None
    ofrece_credito: bool | None = None

    def __post_init__(self) -> None:
        texto = self.texto.strip() if self.texto else None
        object.__setattr__(self, "texto", texto or None)
        object.__setattr__(self, "categorias", tuple(sorted(set(self.categorias))))
        object.__setattr__(self, "tipos", tuple(sorted(set(self.tipos))))
        if self.idioma_atencion is not None and not _IDIOMA.match(self.idioma_atencion):
            raise DatoInvalido(campo="idioma_atencion", regla="formato")
        if self.pagina < 1:
            raise DatoInvalido(campo="pagina", regla="minimo", minimo=1)
        if not 1 <= self.tamano <= 100:
            raise DatoInvalido(campo="tamano", regla="rango", minimo=1, maximo=100)
        if not 100 <= self.radio_m <= RADIO_MAXIMO_M:
            raise DatoInvalido(campo="radio_m", regla="rango", minimo=100, maximo=RADIO_MAXIMO_M)
        if (
            self.precio_min is not None
            and self.precio_max is not None
            and self.precio_min > self.precio_max
        ):
            raise DatoInvalido(campo="precio_min", regla="mayor_que", otro="precio_max")
        if self.orden is OrdenBusqueda.DISTANCIA and self.cerca_de is None:
            raise DatoInvalido(campo="orden", regla="requiere", requiere="lat, lon")
        if self.orden is OrdenBusqueda.RELEVANCIA and self.texto is None:
            raise DatoInvalido(campo="orden", regla="requiere", requiere="texto")

    def filtro_atributos(self) -> dict[str, Any] | None:
        """Objeto para `atributos @> filtro` (índice GIN), o None si no hay filtros de atributos.

        Usa los mismos nombres que `AtributosServicio.a_json()`.
        """
        comunes = {
            clave: valor
            for clave, valor in (
                ("accesible", self.accesible),
                ("mascotas", self.mascotas),
                ("apto_ninos", self.apto_ninos),
            )
            if valor is not None
        }
        if self.idioma_atencion:
            comunes["idiomas_atencion"] = [self.idioma_atencion]
        filtro: dict[str, Any] = {"comunes": comunes} if comunes else {}
        if self.opcion_dietaria:
            filtro["gastronomia"] = {"opciones_dietarias": [self.opcion_dietaria.value]}
        if self.nivel_fisico:
            filtro["experiencia"] = {"nivel_fisico": self.nivel_fisico.value}
        pagos: dict[str, Any] = {}
        if self.acepta_pago_digital is not None:
            pagos["acepta_pago_digital"] = self.acepta_pago_digital
        if self.ofrece_credito is not None:
            pagos["credito"] = {"ofrece": self.ofrece_credito}
        if pagos:
            filtro["pagos"] = pagos
        return filtro or None
