from datetime import datetime, timedelta

from domain.reglas import ZONA


class RelojSistema:
    def ahora(self) -> datetime:
        return datetime.now(ZONA)


class RelojFijo:
    """Para pruebas y demos: la hora solo cambia cuando se avanza a mano."""

    def __init__(self, ahora: datetime):
        self._ahora = ahora

    def ahora(self) -> datetime:
        return self._ahora

    def avanzar(self, **delta: float) -> None:
        self._ahora += timedelta(**delta)
