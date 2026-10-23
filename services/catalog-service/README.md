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
docker compose -f docker-compose.dev.yml up -d   # PostGIS, Valkey, RabbitMQ y SeaweedFS
uv sync                                          # instala dependencias (incluye dev)
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8002
uv run alembic upgrade head                      # aplicar migraciones (incluye las zonas iniciales)
uv run pytest                                    # unitarias + integración (PostGIS en testcontainers)
uv run pytest -m "not integration"               # solo unitarias, sin Docker
uv run ruff check . && uv run ruff format --check .
```

Los puertos de `docker-compose.dev.yml` (5434, 6380, 5673, 15673 y 8333) no chocan con los de iam-service, así que ambos entornos pueden correr a la vez. Las pruebas de integración levantan su propio PostGIS efímero y no tocan la base de desarrollo; sin Docker se omiten.

Las zonas iniciales (migración `0002`) son rectángulos **aproximados** que no se superponen; la Entidad los corrige desde la API. Si dos zonas cubren un mismo punto, el servicio queda en la de menor área.

## Endpoints implementados

El servicio atiende bajo `/api/catalog` (el mismo prefijo del Gateway) y `/health` y `/metrics` en la raíz, como define el contrato. Detalle en [`catalog.yaml`](../../contracts/openapi/catalog.yaml); una prueba verifica que toda ruta implementada esté en el contrato.

| Ruta | Caso de uso | Notas |
|---|---|---|
| `GET /api/catalog/servicios` | UC7 | Pública, paginada |
| `GET /api/catalog/servicios/{id}` | UC9 | Pública; incluye alertas vigentes del servicio y de su zona, `atributos` en el idioma pedido con sus `etiquetas` y `aviso_pagos` |
| `GET /api/catalog/buscar` | UC8 | Pública; texto, categorías, tipos, zona, precio y su unidad, cercanía en metros y filtros de atributos (ver abajo); caché de 300 s en Valkey |
| `GET /api/catalog/zonas` | Filtros | Pública |
| `GET /api/catalog/alertas` | UC26 | Pública; vigentes, de mayor a menor nivel |
| `GET /api/catalog/mapa/servicios` | UC16 | Pública; GeoJSON recortado a `bbox`; con zoom < 13 agrupa en el servidor (caché de 300 s) |
| `GET /api/catalog/mapa/zonas` | UC16 | Pública; polígonos simplificados según el zoom |
| `GET /api/catalog/mapa/alertas` | UC16, UC26 | Pública; puntos (alertas de servicio) y polígonos (de zona) |
| `POST /api/catalog/servicios` | UC17 | Prestador activo; `tipo`, `unidad_tarifa` y `atributos` por tipo (ver abajo); `Idempotency-Key`; publica `servicio.publicado` (outbox) |
| `PUT /api/catalog/servicios/{id}` | UC18 | Dueño; `If-Match` e `Idempotency-Key` |
| `POST /api/catalog/servicios/{id}/desactivar`, `/reactivar` | UC18 | Dueño; `If-Match`; repetir no publica nada |
| `GET /api/catalog/prestador/servicios` | UC18 | Sus servicios, inactivos incluidos, en ambos idiomas |
| `GET`, `PUT /api/catalog/prestador/perfil` | UC4 | Teléfono, dirección y política de cancelación; `If-Match` |
| `POST /api/catalog/prestador/imagenes` | UC17 | URL firmada de SeaweedFS (JPEG/PNG/WebP, 5 MB, 10 min) |
| `GET /api/catalog/geocodificar` | UC17 | Rol Prestador; Nominatim con caché de 7 días y 1 petición/s entre réplicas |
| `POST /api/catalog/zonas` | Zonas | Entidad o Admin; reasigna los servicios que cubre; `CODIGO_EXISTENTE` 409. Crear, editar y desactivar guardan `auditoria.registrada` en el outbox |
| `GET`, `PUT /api/catalog/zonas/{id}` | Zonas | Entidad o Admin; polígono completo y textos es/en; `If-Match`; si cambia el polígono reasigna los servicios |
| `POST /api/catalog/zonas/{id}/desactivar` | Zonas | Entidad o Admin; `If-Match`; con alertas vigentes `ZONA_EN_USO` 409; sus servicios pasan a otra zona o quedan sin zona |
| `GET /health` | RNF-01 | `200` si PostgreSQL responde, `503` si no. Valkey y RabbitMQ no se revisan: sin caché la búsqueda sigue y los eventos esperan en el outbox (ESC-01) |
| `GET /metrics` | RNF-12 | Prometheus |

## Idioma (español e inglés)

El sistema funciona completo en ambos idiomas según `Accept-Language` (español por defecto) y lo informa en `Content-Language`:

* **Textos del sistema** (mensajes de error y etiquetas de categorías y niveles): catálogo en [`app/api/i18n/`](./app/api/i18n/). Una prueba falla si una regla de validación, un error o un valor fijo no tiene texto en los dos idiomas.
* **Textos de usuarios** (nombres, descripciones, alertas, zonas): se guardan como `{"es": ..., "en": ...}`; si falta el inglés se muestra el español. La búsqueda de texto usa el diccionario del idioma pedido (`spanish` / `english`) sin tildes.

## Mapa (OpenStreetMap)

Las capas salen en GeoJSON (RFC 7946, `application/geo+json`), siempre en `[lon, lat]`, listas para `L.geoJSON` de Leaflet sobre teselas de OSM. El zoom define la escala: un píxel equivale a `360 / (256·2^zoom)` grados ([`escala_mapa.py`](./app/application/dto/escala_mapa.py)).

* **Servicios:** con zoom < 13 se agrupan en celdas de unos 64 px y la vista se amplía al borde de las celdas, para que los grupos no cambien al mover el mapa y vistas cercanas compartan caché. Desde zoom 13 llegan uno a uno (hasta 1000). El recorte usa un índice GIST en `geometry` (migración `0003`), exacto en grados.
* **Zonas:** se simplifican con tolerancia de un píxel (`ST_SimplifyPreserveTopology`); nunca se cruzan ni desaparecen.
* **Alertas:** no se cachean. La búsqueda y el mapa comparten la generación de caché (`catalog:gen`): un cambio del catálogo invalida ambos.

## Escritura del prestador

* **Identidad:** `X-Usuario-Id` y `X-Usuario-Rol`, que pone Traefik tras validar el JWT. Sin ellas, `401 NO_AUTENTICADO`; otro rol, `403 ROL_NO_PERMITIDO`. El perfil existe cuando iam aprueba al prestador (`prestador.aprobado`); antes, o si está suspendido, `403 PERFIL_INACTIVO`. Un suspendido puede leer su perfil y sus servicios, pero no escribir.
* **Concurrencia:** cada respuesta trae `ETag: "n"` y cada edición exige `If-Match` (sin él, `428`; con una versión vieja, `409` con el `ETag` actual).
* **Formularios sin conexión:** con `Idempotency-Key` un reenvío devuelve la misma respuesta (`Idempotent-Replayed: true`) sin repetir la operación, durante 48 h. La clave vale por usuario y operación (`idem:catalog:{usuario}:{método}:{ruta}:{clave}` en Valkey).
* **Eventos:** el cambio y `servicio.publicado` se guardan en la misma transacción (tabla `outbox`); el relay que los publica en RabbitMQ llega con la mensajería. Tras confirmar se invalida la caché de búsqueda y mapa.
* **Bloqueos:** toda escritura bloquea primero el perfil y luego el servicio (`SELECT ... FOR UPDATE`), siempre en ese orden. El panel lee sin bloquear.
* **Imágenes:** la PWA sube directo a SeaweedFS con una URL firmada que incluye el tipo y el tamaño; cada imagen queda en `{prestador_id}/{uuid}.{ext}` y un servicio solo acepta imágenes de la carpeta de su prestador. `docker-compose.dev.yml` levanta SeaweedFS en el puerto 8333 y crea el bucket.

## Tipos de servicio y atributos

Cada oferta tiene un **`tipo`** (21 tipos, ver `TipoServicio` en el [contrato](../../contracts/openapi/catalog.yaml)) que define su categoría y qué datos pide el formulario. La categoría ya no se envía: sale del tipo. Se suma la categoría **`TRANSPORTE`** (lanchas y traslados).

* **Ofertas combinadas:** cada cosa que se reserva por separado es un servicio distinto. Un hostal con tour y restaurante registra tres servicios, cada uno con su tarifa, aforo, reservas y reseñas. Lo que viene incluido y no se reserva aparte (desayuno, guía, transporte) es un atributo.
* **`unidad_tarifa`** acompaña a `tarifa_base`: `POR_PERSONA`, `POR_NOCHE`, `POR_GRUPO`, `POR_UNIDAD`, `POR_HORA` o `POR_DIA`.
* **`atributos`** (columna JSONB, migración `0004`) agrupa lo propio de cada tipo en bloques. Cada tipo exige su bloque principal y rechaza los que no le corresponden (`400 bloque_obligatorio` / `bloque_no_permitido`):

| Bloque | Para | Contenido |
|---|---|---|
| `comunes` | Todos | Horario, idiomas de atención, qué incluye y qué no, accesibilidad, mascotas, apto para niños, prácticas y certificación sostenibles |
| `alojamiento` | Hotel, hostal, posada, glamping, apartamento | Check-in y check-out, habitaciones por tipo y capacidad, amenidades, desayuno |
| `experiencia` | Tours, senderismo, deportes, avistamiento, experiencias culturales y comunitarias | Duración, nivel físico, punto de encuentro, edad mínima, tamaño de grupo (no supera el aforo), guía e idiomas, qué llevar, requisitos |
| `gastronomia` | Restaurante, café o bar | Tipos de cocina, opciones dietarias, rango de precio por persona, reserva, puestos, domicilio |
| `entrada` | Parques, playas, museos, eventos | Tarifas por tipo de visitante, temporadas de cierre, reglas, servicios en el sitio |
| `alquiler` | Alquiler de equipo | Equipos, depósito, documento |
| `transporte` | Lancha y traslado terrestre | Origen, destino, duración, capacidad, horarios, chaleco salvavidas |
| `pagos` | Todos (la PWA lo sugiere en experiencias, entradas y transporte) | Ver abajo |

**Dinero y pagos en el lugar (`pagos`):** en sitios alejados puede no haber señal para pagar ni cajeros. El prestador informa la señal de internet (`CON_SENAL`, `INTERMITENTE`, `SIN_SENAL`), los medios que acepta (efectivo, tarjeta, transferencia como Nequi, Daviplata o Bre-B), qué recomienda llevar (`EFECTIVO`, `DIGITAL` o `CUALQUIERA`, que debe coincidir con los medios aceptados), si ofrece **crédito** (cubre el gasto y el turista le paga después, al recuperar señal o pasar por un cajero, con plazo y condiciones) y si hay **cajeros** cerca o dónde está el más cercano. El crédito es un acuerdo entre turista y prestador: la plataforma lo informa, no lo cobra ni lo garantiza.

Textos en `{"es", "en"}`, horas `"HH:MM"` e idiomas en ISO 639-1.

**Lectura pública:**

* **Resultados y listados** traen `tipo` y `unidad_tarifa` con sus etiquetas.
* **Ficha** (`GET /servicios/{id}`): `atributos` con los mismos bloques, pero con los textos ya en el idioma pedido; los códigos fijos (`DE_MAR`, `SIN_SENAL`...) se mantienen y su texto va en `etiquetas`. Si el servicio informó `pagos`, `aviso_pagos` trae una frase lista para mostrar o para el chatbot, por ejemplo: *«Lleva efectivo: no hay señal de internet y no hay cajeros cerca (el más cercano: Parque de Minca, a 8 km). El prestador ofrece crédito…»*. `importante=true` (sin señal o intermitente, solo efectivo o sin cajeros) indica que la PWA debe destacarlo.
* **Filtros de `/buscar`:** `tipo` (uno o varios), `unidad_tarifa`, `idioma_atencion`, `accesible`, `mascotas`, `apto_ninos`, `opcion_dietaria`, `nivel_fisico`, `acepta_pago_digital` y `ofrece_credito`. Los de atributos se combinan en una sola contención `atributos @> {...}` sobre el índice GIN. Un sí/no filtra por lo informado: `accesible=false` trae los que dijeron que no, no los que no lo informaron. Todos forman parte de la clave de la caché.

## Correlación

Cada respuesta lleva `X-Correlation-ID` (el que envía Traefik o uno nuevo) y los logs salen en JSON con ese mismo identificador.

Imagen de contenedor (multi-stage):

```bash
docker build -t catalog-service:dev .
docker run --env-file .env -p 8002:8002 catalog-service:dev
```
