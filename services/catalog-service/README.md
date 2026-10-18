# catalog-service

**Módulo 2: Catálogo, GIS & Inteligencia de Destino** · Responsable: Luis Fernando Barraza Sanchez (@luifdo)

Catálogo de atractivos, actividades y perfiles de prestador; búsqueda multicriterio y geoespacial con PostGIS y OpenStreetMap; analítica de demanda y capacidad de carga a partir de eventos; tableros, reportes y alertas oficiales; correos transaccionales. Absorbe el antiguo Módulo 6 (Analítica & Destino).

| Aspecto | Valor |
|---|---|
| Casos de uso | UC7, UC8, UC9, UC16, UC17, UC18, UC22, UC23, UC24, UC25, UC26, UC36, UC38 |
| Requerimientos funcionales | RF-01, RF-02, RF-05, RF-07, RF-08, RF-11, RF-13 |
| Requerimientos no funcionales | RNF-01, RNF-02, RNF-03, RNF-06, RNF-13 |
| Escenarios de calidad | ESC-02, ESC-03, ESC-08, ESC-09 |
| Persistencia | PostgreSQL + PostGIS — base lógica `catalog_db`; caché en Valkey |
| Lenguaje / framework | Python 3.12 + FastAPI (orientado a objetos, arquitectura hexagonal) |
| Puerto interno | `8002` |
| Prefijo en el Gateway (Traefik) | `/api/catalog` |
| Réplicas en k3s | 2 (HPA hasta 6) |
| Contrato REST | [`contracts/openapi/catalog.yaml`](../../contracts/openapi/) |

## Eventos

**Publica:**
* `servicio.publicado.v1` (dueño y aforo para booking-service)
* `auditoria.registrada.v1`

**Consume:**
* `prestador.aprobado.v1` (crea o reactiva el perfil del prestador)
* `prestador.suspendido.v1` (desactiva el perfil y sus servicios)
* `reserva.solicitada.v1`, `reserva.modificada.v1`, `reserva.confirmada.v1`, `reserva.rechazada.v1`, `reserva.cancelada.v1`, `reserva.finalizada.v1` (correos y demanda)
* `resena.publicada.v1` (calificación promedio y métricas)

Esquemas en [`contracts/events/`](../../contracts/events/).

## Estructura (arquitectura hexagonal)

Solo `app/` tiene `__init__.py`; las subcarpetas son paquetes de espacio de nombres (PEP 420). Cada carpeta se crea en el paso que la implementa, así que algunas de este árbol todavía no existen.

```
app/
├── __init__.py
├── main.py              # composición: crea la app FastAPI, el engine y /metrics
├── config.py            # Settings (pydantic-settings) leídos de variables de entorno / .env
├── domain/              # núcleo puro, sin dependencias de frameworks
│   ├── entities/
│   ├── value_objects/
│   └── ports/           # interfaces (Protocols) que implementa la infraestructura
├── application/
│   └── use_cases/       # una clase por caso de uso
├── infrastructure/      # adaptadores que implementan los puertos
│   ├── persistence/     # SQLAlchemy async + GeoAlchemy2 sobre catalog_db (PostGIS)
│   ├── cache/           # Valkey (búsquedas, idempotencia de formularios)
│   ├── messaging/       # RabbitMQ (outbox, publicador y consumidores)
│   ├── notifications/   # correo SMTP
│   ├── storage/         # S3 (SeaweedFS, imágenes del catálogo)
│   └── clients/         # HTTP hacia booking, iam y Nominatim
└── api/                 # adaptador HTTP
    ├── routers/
    ├── schemas/         # modelos Pydantic de request/response
    └── dependencies.py  # cableado de casos de uso con sus adaptadores
migrations/              # Alembic (async)
tests/
```

## Ejecución

Requiere [uv](https://docs.astral.sh/uv/) y Python 3.12 (`uv python install 3.12`).

```bash
docker compose -f docker-compose.dev.yml up -d   # PostGIS, Valkey y RabbitMQ de desarrollo
uv sync                                          # instala dependencias (incluye dev)
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8002
uv run alembic upgrade head                      # aplicar migraciones (incluye las zonas iniciales)
uv run pytest                                    # unitarias + integración (PostGIS en testcontainers)
uv run pytest -m "not integration"               # solo unitarias, sin Docker
uv run ruff check . && uv run ruff format --check .
```

Los puertos de `docker-compose.dev.yml` (5434, 6380, 5673 y 15673) no chocan con los de iam-service, así que ambos entornos pueden correr a la vez. Las pruebas de integración levantan su propio PostGIS efímero y no tocan la base de desarrollo; sin Docker se omiten.

Las zonas iniciales (migración `0002`) son rectángulos **aproximados** que no se superponen; la Entidad los corrige desde la API. Si dos zonas cubren un mismo punto, el servicio queda en la de menor área.

Endpoints operativos:

* `GET /health`: `200` si PostgreSQL responde a `SELECT 1`, `503` si no. Valkey y RabbitMQ no se revisan: sin caché la búsqueda sigue funcionando y los eventos esperan en el outbox (ESC-01).
* `GET /metrics`: métricas Prometheus (prometheus-fastapi-instrumentator).

Imagen de contenedor (multi-stage):

```bash
docker build -t catalog-service:dev .
docker run --env-file .env -p 8002:8002 catalog-service:dev
```
