from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración del servicio, cargada desde variables de entorno o un archivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "catalog-service"
    service_port: int = 8002
    environment: str = "development"

    database_url: str = (
        "postgresql+asyncpg://catalog_user:catalog_password@localhost:5434/catalog_db"
    )
    database_health_timeout_seconds: float = 2.0

    valkey_url: str = "redis://localhost:6380/0"

    rabbitmq_url: str = "amqp://guest:guest@localhost:5673/"
    events_exchange: str = "turismo.eventos"


@lru_cache
def get_settings() -> Settings:
    return Settings()
