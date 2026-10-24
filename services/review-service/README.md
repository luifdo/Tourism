# review-service

**Módulo 4: Reseñas & Moderación** · Responsable: Luis Fernando Barraza Sanchez (@luifdo)

Calificaciones y reseñas de turistas con reserva finalizada, respuestas públicas de prestadores, reporte de reseñas inapropiadas (UC39) y moderación manual del Administrador (UC29).

| Aspecto | Valor |
|---|---|
| Casos de uso | UC15, UC21, UC29, UC39 |
| Requerimientos funcionales | RF-14 |
| Requerimientos no funcionales | RNF-01, RNF-10 |
| Escenarios de calidad | ESC-01 |
| Persistencia | PostgreSQL con JSONB — base lógica `review_db` |
| Lenguaje / framework | Python 3.12 + FastAPI (orientado a objetos, arquitectura hexagonal) |
| Puerto interno | `8004` |
| Prefijo en el Gateway (Traefik) | `/api/reviews` |
| Réplicas en k3s | 1 (HPA hasta 3) |
| Contrato REST | [`contracts/openapi/review.yaml`](../../contracts/openapi/review.yaml) |

## Eventos

**Publica** (con outbox, como catalog-service):
* `resena.publicada.v1`: al crear o editar una reseña, y al volver a publicar una oculta.
* `resena.ocultada.v1`: cuando el Administrador la oculta (catalog la quita del promedio).
* `auditoria.registrada.v1`: decisiones de moderación (MODERACION) y accesos denegados (ACCESS_DENIED).

**Consume:**
* `reserva.finalizada.v1` en `review.elegibilidad`: habilita la reseña del turista para ese servicio.
* `servicio.publicado.v1` en `review.servicios`: qué prestador es dueño de cada servicio (responder y reportar).

## Reglas principales

* Una reseña por turista y servicio, solo con una reserva finalizada; editable por su autor.
* Autor anónimo: "Turista verificado" y el mes de la visita.
* Un reporte no oculta la reseña: entra en la cola del Administrador. Pasa a `EN_REVISION` (oculta) al tercer reporte o si la reporta el prestador dueño; su nota sigue contando hasta que el Administrador la publique u oculte.

Esquemas en [`contracts/events/`](../../contracts/events/).

## Estructura (arquitectura hexagonal)

Misma estructura que catalog-service (una clase por archivo; solo `app/` tiene `__init__.py`):

```
app/
├── main.py              # composición: crea la app FastAPI e inyecta los adaptadores
├── worker.py            # relay del outbox y consumidores (proceso aparte)
├── domain/              # entidades y reglas de negocio puras, sin dependencias de frameworks
├── application/         # casos de uso (una clase por caso de uso), DTO y puertos
├── infrastructure/      # adaptadores: persistencia (SQLAlchemy), mensajería (aio-pika), observabilidad
└── api/                 # routers FastAPI (implementan el contrato OpenAPI), esquemas, errores e i18n
migrations/              # Alembic
tests/
├── unit/
└── integration/
```

## Ejecución

Servicio en Python 3.12 + FastAPI, empaquetado como contenedor y desplegado en Kubernetes (k3s) según el [Plan de Implementación](../../Documents/Pages/Plan_de_Implementacion.md) §7. El código, el `Dockerfile` y los manifiestos se agregan en la Fase 4.
