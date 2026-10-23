"""Worker de catalog-service: trabajo en segundo plano, separado de la API.

Corre con la misma imagen y otro comando (`python -m app.worker`), en su propio Deployment.
Así la publicación de eventos (y, desde el paso 10, los consumidores) no compite con las
peticiones de los turistas, y los reinicios o el escalado de la API no lo interrumpen.

Expone sus métricas en `WORKER_METRICS_PORT` (/metrics), que también sirve de sonda de vida.
"""

import asyncio
import contextlib
import logging
import signal
from datetime import timedelta

from prometheus_client import start_http_server

from app.application.use_cases.publicar_eventos_pendientes import PublicarEventosPendientes
from app.config import Settings, get_settings
from app.infrastructure.messaging.publicador_rabbitmq import PublicadorRabbitMQ
from app.infrastructure.messaging.relay_outbox import RelayOutbox
from app.infrastructure.observabilidad.configurar_logs import configurar_logs
from app.infrastructure.persistence.database import build_engine, build_session_factory
from app.infrastructure.persistence.repositorios.outbox_pendiente import SqlOutboxPendiente
from app.infrastructure.reloj import RelojSistema

logger = logging.getLogger(__name__)


def construir_relay(
    settings: Settings, outbox: SqlOutboxPendiente, publicador: PublicadorRabbitMQ
) -> RelayOutbox:
    reloj = RelojSistema()
    return RelayOutbox(
        publicar=PublicarEventosPendientes(outbox, publicador, reloj, settings.outbox_lote),
        outbox=outbox,
        reloj=reloj,
        lote=settings.outbox_lote,
        intervalo_segundos=settings.outbox_intervalo_segundos,
        espera_maxima_segundos=settings.outbox_espera_maxima_segundos,
        retencion=timedelta(days=settings.outbox_retencion_dias),
    )


async def correr(settings: Settings) -> None:
    detener = asyncio.Event()
    bucle = asyncio.get_running_loop()
    for senal in (signal.SIGTERM, signal.SIGINT):
        # En Windows no hay manejadores de señales en el bucle: ahí se corta con Ctrl+C.
        with contextlib.suppress(NotImplementedError):
            bucle.add_signal_handler(senal, detener.set)

    engine = build_engine(settings.database_url)
    publicador = PublicadorRabbitMQ(
        settings.rabbitmq_url, settings.events_exchange, settings.rabbitmq_timeout_seconds
    )
    relay = construir_relay(settings, SqlOutboxPendiente(build_session_factory(engine)), publicador)
    logger.info("Worker iniciado: relay del outbox hacia %s", settings.events_exchange)
    try:
        await relay.ejecutar(detener)
    finally:
        await publicador.cerrar()
        await engine.dispose()
        logger.info("Worker detenido")


def main() -> None:
    settings = get_settings()
    configurar_logs(f"{settings.service_name}-worker", settings.log_level)
    start_http_server(settings.worker_metrics_port)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(correr(settings))


if __name__ == "__main__":
    main()
