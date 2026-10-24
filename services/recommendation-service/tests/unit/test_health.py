from fastapi.testclient import TestClient

from src.main import app

cliente = TestClient(app)


def test_health_responde_200():
    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_metrics_expone_formato_prometheus():
    cliente.get("/health")

    respuesta = cliente.get("/metrics")

    assert respuesta.status_code == 200
    assert "http_requests_total" in respuesta.text
