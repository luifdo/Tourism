# Stack elegido

> Módulo 5 · [Índice](./README.md)

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje | Python 3.12 | Decisión del proyecto (ADR-006). |
| Framework | FastAPI | Decisión del proyecto; genera el `/openapi.json` y valida la entrada con Pydantic. |
| Servidor | Uvicorn | Es el servidor estándar para FastAPI. |
| Base de datos | PostgreSQL 16 | Igual que en el Plan; aquí sin PostGIS porque el módulo no usa datos espaciales. |
| Acceso a datos | SQLAlchemy (+ driver `psycopg`) | Indicado en la estructura hexagonal del servicio. |
| Sesiones | Valkey 8 | Igual que en el Plan. Se usa con el cliente de Redis, que es compatible. |
| Llamadas a otros servicios | `httpx` | Cliente HTTP asíncrono para las tools. |
| Métricas | `prometheus-fastapi-instrumentator` | Expone `/metrics`, que exige RNF-12. |
| Proveedor de IA | Por definir; el primero previsto es Gemini (SDK `google-genai`, Plan §4) | El servicio no depende de un proveedor: se conecta mediante una interfaz propia y cualquiera se puede cambiar o agregar. |
| Pruebas | `pytest` | Indicado en el Plan §8. |
| Dependencias | `pip` + `requirements.txt` | Lo más simple para empezar. |

Las versiones exactas se fijan en `requirements.txt` cuando se cree el servicio.

---
[← Arquitectura local](./02-arquitectura-local.md) · [Estructura de carpetas →](./04-estructura.md)
