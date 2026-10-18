"""API de lectura con dobles de las consultas: contrato HTTP, idioma y formato de errores."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_consulta_alertas, get_consulta_servicios, get_consulta_zonas
from app.application.dto.alerta_vista import AlertaVista
from app.application.dto.criterios_busqueda import CriteriosBusqueda, OrdenBusqueda
from app.application.dto.pagina_servicios import PaginaServicios
from app.application.dto.prestador_publico import PrestadorPublico
from app.application.dto.servicio_detalle import ServicioDetalle
from app.application.dto.servicio_resumen import ServicioResumen
from app.application.dto.zona_resumen import ZonaResumen
from app.application.dto.zona_vista import ZonaVista
from app.domain.value_objects.catalogos import Categoria, NivelAlerta
from app.domain.value_objects.geo import Coordenada
from app.domain.value_objects.texto_traducido import TextoTraducido
from app.main import create_app

SERVICIO_ID = uuid4()
MINCA = ZonaResumen(codigo="minca", nombre=TextoTraducido(es="Minca"))
TAYRONA = ZonaResumen(
    codigo="parque-tayrona",
    nombre=TextoTraducido(es="Parque Nacional Natural Tayrona", en="Tayrona National Natural Park"),
)
SERVICIO = ServicioResumen(
    id=SERVICIO_ID,
    nombre=TextoTraducido(es="Tour del café", en="Coffee tour"),
    categoria=Categoria.GASTRONOMIA,
    ubicacion=Coordenada(lat=11.1426, lon=-74.1178),
    tarifa_base=Decimal("85000.50"),
    zona=MINCA,
    calificacion_promedio=4.5,
    total_resenas=2,
    imagen_principal=None,
)
ALERTA = AlertaVista(
    id=uuid4(),
    nivel=NivelAlerta.CRITICA,
    mensaje=TextoTraducido(es="Sendero cerrado"),  # sin traducción: sale en español
    servicio_id=None,
    zona=MINCA,
    fecha_expiracion=datetime(2026, 10, 20, tzinfo=UTC),
)


class ConsultasFalsas:
    def __init__(self) -> None:
        self.criterios: CriteriosBusqueda | None = None
        self.fallar = False

    async def buscar(self, criterios: CriteriosBusqueda) -> PaginaServicios:
        if self.fallar:
            raise RuntimeError("PostGIS no responde")
        self.criterios = criterios
        return PaginaServicios(
            items=(SERVICIO,), pagina=criterios.pagina, tamano=criterios.tamano, total=1
        )

    async def detalle(self, servicio_id: UUID, ahora: datetime) -> ServicioDetalle | None:
        if servicio_id != SERVICIO_ID:
            return None
        return ServicioDetalle(
            resumen=SERVICIO,
            descripcion=TextoTraducido(es="Recorrido por fincas", en="Farm walk"),
            capacidad_aforo_diario=20,
            imagenes_urls=(),
            prestador=PrestadorPublico(
                id=uuid4(),
                razon_social="Café de la Sierra",
                telefono=None,
                politica_cancelacion=TextoTraducido(es="Gratis 24 h antes", en="Free 24 h before"),
            ),
            alertas=(ALERTA,),
        )

    async def activas(self) -> list[ZonaVista]:
        return [
            ZonaVista(uuid4(), TAYRONA.codigo, TAYRONA.nombre, Coordenada(11.3, -74.0)),
            ZonaVista(uuid4(), MINCA.codigo, MINCA.nombre, Coordenada(11.14, -74.11)),
        ]

    async def vigentes(
        self, ahora: datetime, zona: str | None = None, servicio_id: UUID | None = None
    ) -> list[AlertaVista]:
        return [ALERTA]


@pytest.fixture
def consultas() -> ConsultasFalsas:
    return ConsultasFalsas()


@pytest.fixture
def cliente(consultas: ConsultasFalsas) -> Iterator[TestClient]:
    app = create_app()
    for dependencia in (get_consulta_servicios, get_consulta_zonas, get_consulta_alertas):
        app.dependency_overrides[dependencia] = lambda: consultas
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestIdioma:
    def test_busqueda_en_espanol_por_defecto(self, cliente: TestClient) -> None:
        r = cliente.get("/api/catalog/buscar")
        assert r.status_code == 200 and r.headers["content-language"] == "es"
        item = r.json()["items"][0]
        assert (item["nombre"], item["categoria"], item["categoria_etiqueta"]) == (
            "Tour del café",
            "GASTRONOMIA",
            "Gastronomía",
        )
        assert item["tarifa_base"] == 85000.5  # número, no texto
        assert r.json()["disponibilidad_verificada"] is None

    def test_misma_busqueda_en_ingles(self, cliente: TestClient) -> None:
        r = cliente.get("/api/catalog/buscar", headers={"Accept-Language": "en-US,en;q=0.9"})
        assert r.headers["content-language"] == "en"
        item = r.json()["items"][0]
        assert (item["nombre"], item["categoria_etiqueta"]) == ("Coffee tour", "Food & dining")

    def test_detalle_en_ingles_con_textos_sin_traducir(self, cliente: TestClient) -> None:
        r = cliente.get(f"/api/catalog/servicios/{SERVICIO_ID}", headers={"Accept-Language": "en"})
        cuerpo = r.json()
        assert cuerpo["descripcion"] == "Farm walk"
        assert cuerpo["prestador"]["politica_cancelacion"] == "Free 24 h before"
        alerta = cuerpo["alertas"][0]
        assert (alerta["nivel_etiqueta"], alerta["mensaje"]) == ("Critical", "Sendero cerrado")

    def test_zonas_ordenadas_por_nombre_en_el_idioma(self, cliente: TestClient) -> None:
        es = [z["nombre"] for z in cliente.get("/api/catalog/zonas").json()]
        en = [
            z["nombre"]
            for z in cliente.get("/api/catalog/zonas", headers={"Accept-Language": "en"}).json()
        ]
        assert es == ["Minca", "Parque Nacional Natural Tayrona"]
        assert en == ["Minca", "Tayrona National Natural Park"]


class TestParametros:
    def test_filtros_llegan_validados(
        self, cliente: TestClient, consultas: ConsultasFalsas
    ) -> None:
        r = cliente.get(
            "/api/catalog/buscar",
            params={
                "texto": "playa tranquila",
                "categoria": "playa, cultura",
                "zona": "taganga",
                "precio_max": "200000",
                "lat": 11.27,
                "lon": -74.19,
                "radio_m": 2000,
                "orden": "distancia",
            },
        )
        assert r.status_code == 200
        c = consultas.criterios
        assert c is not None
        assert c.categorias == (Categoria.CULTURA, Categoria.PLAYA)
        assert c.cerca_de == Coordenada(lat=11.27, lon=-74.19)
        assert (c.radio_m, c.orden, c.precio_max) == (
            2000,
            OrdenBusqueda.DISTANCIA,
            Decimal("200000"),
        )

    def test_listar_catalogo_usa_una_categoria(
        self, cliente: TestClient, consultas: ConsultasFalsas
    ) -> None:
        cliente.get("/api/catalog/servicios", params={"categoria": "PLAYA", "tamano": 5})
        assert consultas.criterios is not None
        assert (
            consultas.criterios.categorias == (Categoria.PLAYA,) and consultas.criterios.tamano == 5
        )


class TestErrores:
    @pytest.mark.parametrize(
        ("params", "idioma", "mensaje"),
        [
            ({"lat": 11.2}, "es", "El campo «lon» es obligatorio."),
            ({"lat": 11.2}, "en", "The field 'lon' is required."),
            ({"orden": "distancia"}, "en", "The field 'orden' also requires: lat, lon."),
            (
                {"categoria": "PLAYA,MONTAÑA"},
                "es",
                "El campo «categoria» no tiene un formato válido.",
            ),
            ({"radio_m": 10}, "es", "El campo «radio_m» no tiene un formato válido."),
            ({"tamano": 51}, "en", "The field 'tamano' has an invalid format."),
        ],
    )
    def test_validacion_en_el_idioma_pedido(
        self, cliente: TestClient, params: dict, idioma: str, mensaje: str
    ) -> None:
        r = cliente.get("/api/catalog/buscar", params=params, headers={"Accept-Language": idioma})
        assert r.status_code == 400
        assert r.json()["error"] == "VALIDACION" and r.json()["message"] == mensaje
        assert r.headers["content-language"] == idioma

    def test_servicio_inexistente(self, cliente: TestClient) -> None:
        r = cliente.get(f"/api/catalog/servicios/{uuid4()}", headers={"Accept-Language": "en"})
        assert r.status_code == 404
        assert r.json()["error"] == "NO_ENCONTRADO"
        assert r.json()["message"].startswith("The requested resource")

    def test_error_inesperado_no_filtra_detalles(
        self, cliente: TestClient, consultas: ConsultasFalsas
    ) -> None:
        consultas.fallar = True
        r = cliente.get("/api/catalog/buscar", headers={"X-Correlation-ID": "abc-123"})
        assert r.status_code == 500
        assert r.json()["error"] == "ERROR_INTERNO" and "PostGIS" not in r.json()["message"]
        assert r.json()["correlation_id"] == "abc-123"
        assert r.headers["x-correlation-id"] == "abc-123"


class TestCorrelacion:
    def test_se_propaga_el_id_recibido(self, cliente: TestClient) -> None:
        r = cliente.get(f"/api/catalog/servicios/{uuid4()}", headers={"X-Correlation-ID": "corr-1"})
        assert r.headers["x-correlation-id"] == "corr-1"
        assert r.json()["correlation_id"] == "corr-1"

    @pytest.mark.parametrize("recibido", [None, "con espacios y ;", "x" * 101])
    def test_se_genera_uno_si_falta_o_es_invalido(
        self, cliente: TestClient, recibido: str | None
    ) -> None:
        cabeceras = {"X-Correlation-ID": recibido} if recibido else {}
        r = cliente.get("/api/catalog/zonas", headers=cabeceras)
        assert str(UUID(r.headers["x-correlation-id"])) == r.headers["x-correlation-id"]


def test_las_alertas_expiran_en_el_futuro() -> None:
    # Sanidad del doble usado arriba: evita que una prueba pase con datos imposibles.
    assert ALERTA.fecha_expiracion > datetime(2026, 10, 18, tzinfo=UTC) - timedelta(days=1)
