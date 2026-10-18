# iam-service

**Módulo 1: Seguridad & IAM** · Responsable: Valentina Sarait Nieves Hernandez (@nievesita)

Autenticación JWT (RS256), verificación de tokens para el API Gateway (ForwardAuth), control de acceso por roles (RBAC), verificación de prestadores (RNT, RUT), consentimiento de datos personales (Ley 1581) y bitácora de auditoría inmutable.

| Aspecto | Valor |
|---|---|
| Casos de uso | UC1, UC2, UC3, UC4, UC6, UC27, UC28, UC32, UC33, UC37 |
| Requerimientos funcionales | RF-08, RF-09, RF-12 |
| Requerimientos no funcionales | RNF-04, RNF-10 |
| Escenarios de calidad | ESC-04 |
| Persistencia | PostgreSQL — base lógica `iam_db`; documentos en SeaweedFS (bucket `documentos-verificacion`); tokens revocados en Valkey |
| Lenguaje / framework | Python 3.12 + FastAPI (orientado a objetos, arquitectura hexagonal) |
| Puerto interno | `8001` |
| Prefijo en el Gateway (Traefik) | `/api/iam` |
| Réplicas en k3s | 2 (HPA hasta 4) |
| Contrato REST | [`contracts/openapi/iam.yaml`](../../contracts/openapi/) |

## Eventos

**Publica:**
* `prestador.aprobado.v1`

**Consume:**
* `auditoria.registrada.v1` (de catalog, booking y review)

Esquemas en [`contracts/events/`](../../contracts/events/).

## Estructura (arquitectura hexagonal)

```
app/
├── main.py              # composición: crea la app FastAPI, el engine y /metrics
├── config.py            # Settings (pydantic-settings) leídos de variables de entorno / .env
├── domain/              # núcleo puro, sin dependencias de frameworks
│   ├── entities/
│   ├── value_objects/
│   └── ports/           # interfaces (Protocols) que implementa la infraestructura
├── application/
│   └── use_cases/       # una clase por caso de uso
├── infrastructure/      # adaptadores que implementan los puertos
│   ├── persistence/     # SQLAlchemy async sobre iam_db
│   ├── security/        # Argon2 (contraseñas) y PyJWT (RS256)
│   ├── cache/           # Valkey (tokens revocados)
│   ├── messaging/       # RabbitMQ
│   └── storage/         # S3 (SeaweedFS)
└── api/                 # adaptador HTTP
    ├── routers/
    ├── schemas/         # modelos Pydantic de request/response
    └── dependencies.py  # cableado de casos de uso con sus adaptadores
migrations/              # Alembic (async)
tests/
```

## Ejecución

Requiere [uv](https://docs.astral.sh/uv/) y Python 3.12.

```bash
uv sync                                   # instala dependencias (incluye dev)
cp .env.example .env                      # ajustar DATABASE_URL y demás
uv run uvicorn app.main:app --reload --port 8001
uv run pytest                             # pruebas
uv run ruff check . && uv run ruff format --check .
uv run alembic upgrade head               # aplicar migraciones
```

Endpoints operativos:

* `GET /health`: `200` si PostgreSQL responde a `SELECT 1`, `503` si no.
* `GET /metrics`: métricas Prometheus (prometheus-fastapi-instrumentator).

Imagen de contenedor (multi-stage):

```bash
docker build -t iam-service:dev .
docker run --env-file .env -p 8001:8001 iam-service:dev
```

Las llaves JWT (`keys/private.pem`, `keys/public.pem`) no se versionan ni se copian en la imagen; se montan en tiempo de ejecución.
