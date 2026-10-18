from dataclasses import dataclass

from app.domain.ports.health import DatabaseProbe


@dataclass(frozen=True)
class HealthReport:
    database: bool

    @property
    def healthy(self) -> bool:
        return self.database


class CheckHealth:
    def __init__(self, database: DatabaseProbe) -> None:
        self._database = database

    async def execute(self) -> HealthReport:
        return HealthReport(database=await self._database.ping())
