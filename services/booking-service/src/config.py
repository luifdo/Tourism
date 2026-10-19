"""Configuración por variables de entorno (ver .env.example)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_port: int = 8003
    # "memoria": sin Postgres ni RabbitMQ (pruebas y demo). "postgres" llega en el Sprint 5.
    modo_persistencia: str = "memoria"
    plazo_respuesta_horas: int = 48
    # Solo en modo memoria: carga un servicio de ejemplo y habilita las rutas /dev para la demo.
    datos_demo: bool = True
