from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.infrastructure.http import health


def create_app() -> FastAPI:
    app = FastAPI(title="recommendation-service", version="1.0.0")
    app.include_router(health.router)
    # Expone GET /metrics en formato Prometheus (RNF-12).
    Instrumentator().instrument(app).expose(app)
    return app


app = create_app()
