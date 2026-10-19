"""Sondas de Kubernetes y métricas de Prometheus (RNF-01)."""

import time

from fastapi import APIRouter, FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest

router = APIRouter(tags=["Operación"])

REGISTRO = CollectorRegistry()
PETICIONES = Counter(
    "booking_http_peticiones_total", "Peticiones HTTP atendidas", ["metodo", "ruta", "estado"], registry=REGISTRO
)
LATENCIA = Histogram(
    "booking_http_latencia_segundos", "Latencia de las peticiones HTTP", ["metodo", "ruta"], registry=REGISTRO
)


@router.get("/health", summary="Estado del servicio (sondas de Kubernetes)")
async def health():
    return {"estado": "ok"}


@router.get("/metrics", summary="Métricas para Prometheus")
async def metrics():
    return Response(generate_latest(REGISTRO), media_type=CONTENT_TYPE_LATEST)


def registrar_metricas(app: FastAPI) -> None:
    @app.middleware("http")
    async def _medir(request: Request, siguiente):
        inicio = time.perf_counter()
        respuesta = await siguiente(request)
        # La plantilla de la ruta (p. ej. /api/bookings/{reserva_id}) evita una serie por cada id.
        ruta = getattr(request.scope.get("route"), "path", "desconocida")
        LATENCIA.labels(request.method, ruta).observe(time.perf_counter() - inicio)
        PETICIONES.labels(request.method, ruta, str(respuesta.status_code)).inc()
        return respuesta
