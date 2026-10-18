"""Toda ruta que expone el servicio debe estar en el contrato (contrato antes que código)."""

from pathlib import Path

import yaml
from fastapi.routing import APIRoute

from app.main import create_app

CONTRATO = Path(__file__).resolve().parents[5] / "contracts" / "openapi" / "catalog.yaml"
PREFIJO = "/api/catalog"


def rutas_del_contrato() -> set[tuple[str, str]]:
    contrato = yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))
    rutas = set()
    for ruta, operaciones in contrato["paths"].items():
        for metodo in operaciones:
            if metodo in {"get", "post", "put", "patch", "delete"}:
                rutas.add((metodo.upper(), ruta))
    return rutas


def rutas_de_la_app() -> set[tuple[str, str]]:
    rutas = set()
    for ruta in create_app().routes:
        if isinstance(ruta, APIRoute):
            camino = ruta.path.removeprefix(PREFIJO) or "/"
            rutas |= {(metodo, camino) for metodo in ruta.methods}
    return rutas


def test_cada_ruta_implementada_esta_en_el_contrato() -> None:
    sin_contrato = rutas_de_la_app() - rutas_del_contrato()
    assert not sin_contrato, f"Rutas sin contrato: {sorted(sin_contrato)}"
