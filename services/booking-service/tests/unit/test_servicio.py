from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from domain.disponibilidad import DisponibilidadCupo
from domain.errores import NoDisponible
from domain.reglas import ZONA
from domain.servicio import ServicioRef, disponibilidad_en

AHORA = datetime(2026, 11, 1, 10, 0, tzinfo=ZONA)
FECHA = date(2026, 11, 5)


def servicio(version: int = 1, activo: bool = True) -> ServicioRef:
    return ServicioRef(uuid4(), uuid4(), uuid4(), 20, Decimal("50000"), activo, version)


def dia(s: ServicioRef, disponibles: int, fecha: date = FECHA) -> DisponibilidadCupo:
    d = DisponibilidadCupo.abrir(s.servicio_id, fecha, 10)
    d.cupos_disponibles = disponibles
    return d


class TestServicioRef:
    def test_es_de_compara_con_el_usuario_no_con_el_perfil(self):
        s = servicio()
        assert s.es_de(s.prestador_usuario_id)
        assert not s.es_de(s.prestador_id)

    def test_inactivo(self):
        with pytest.raises(NoDisponible):
            servicio(activo=False).exigir_activo()

    @pytest.mark.parametrize(("nueva", "actual", "reemplaza"), [(2, 1, True), (1, 1, False), (1, 2, False)])
    def test_solo_reemplaza_versiones_mas_nuevas(self, nueva, actual, reemplaza):
        assert servicio(version=nueva).reemplaza_a(servicio(version=actual)) is reemplaza

    def test_reemplaza_si_no_habia_nada(self):
        assert servicio().reemplaza_a(None)


class TestDisponibilidadEn:
    def test_disponible(self):
        s = servicio()
        assert disponibilidad_en(s, dia(s, 7), FECHA, 2, AHORA) == (7, True)

    def test_cupos_insuficientes(self):
        s = servicio()
        assert disponibilidad_en(s, dia(s, 1), FECHA, 2, AHORA) == (1, False)

    def test_servicio_desconocido_o_dia_cerrado(self):
        s = servicio()
        assert disponibilidad_en(None, None, FECHA, 1, AHORA) == (0, False)
        assert disponibilidad_en(s, None, FECHA, 1, AHORA) == (0, False)

    def test_servicio_inactivo(self):
        s = servicio(activo=False)
        assert disponibilidad_en(s, dia(s, 7), FECHA, 1, AHORA) == (0, False)

    def test_hoy_tiene_cupos_pero_no_admite_solicitudes(self):
        s = servicio()
        hoy = AHORA.date()
        assert disponibilidad_en(s, dia(s, 7, hoy), hoy, 1, AHORA) == (7, False)
