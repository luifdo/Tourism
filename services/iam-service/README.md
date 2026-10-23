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
uv run python -m uvicorn app.main:app --reload --port 8001
uv run pytest                             # pruebas (las marcadas db se omiten si PostgreSQL no responde)
uv run ruff check . && uv run ruff format --check .
uv run alembic upgrade head               # aplicar migraciones
```

> En Windows, Smart App Control puede bloquear `uvicorn.exe` del `.venv`; `python -m uvicorn` evita el problema.

## Endpoints

Operativos:

* `GET /health`: `200` si PostgreSQL responde a `SELECT 1`, `503` si no.
* `GET /metrics`: métricas Prometheus (prometheus-fastapi-instrumentator).

### `POST /api/iam/register` (UC1 + UC6)

Registro de Turistas y Prestadores. Otros roles no se autorregistran.

Cuerpo:

```json
{
  "email": "maria.perez@example.com",
  "password": "Tayrona2026",
  "nombre_completo": "María Pérez",
  "rol": "Turista",
  "habeas_data_aceptado": true,
  "es_mayor_de_edad": true
}
```

`201 Created`: nunca incluye la contraseña ni su hash.

```json
{
  "id": "8fa88503-29e2-4ff7-b47e-bc22f8856bce",
  "email": "maria.perez@example.com",
  "nombre_completo": "María Pérez",
  "rol": "Turista",
  "email_verificado": false,
  "creado_en": "2026-10-23T07:17:49.145181Z"
}
```

Errores, con cuerpo `{"detail": "<mensaje>", "code": "<code>"}`:

| HTTP | `code` | Causa |
|---|---|---|
| 409 | `EMAIL_EN_USO` | Ya existe una cuenta con ese correo |
| 422 | `VALIDACION` | La petición no cumple el esquema (email mal formado, rol no permitido, campo faltante…). Incluye `"errores": [{"campo": "...", "mensaje": "..."}]` |
| 422 | `HABEAS_DATA_REQUERIDO` | No aceptó el tratamiento de datos personales (Ley 1581) |
| 422 | `MAYORIA_DE_EDAD_REQUERIDA` | No declaró ser mayor de edad |
| 422 | `PASSWORD_INVALIDA` | La contraseña no tiene entre 8 y 128 caracteres con al menos una letra y un número |
| 422 | `NOMBRE_INVALIDO` | El nombre no tiene entre 2 y 150 caracteres |

Los 422 de `VALIDACION` nunca devuelven el valor enviado, para no repetir la contraseña.

### `POST /api/iam/login` (UC2)

Cuerpo JSON (no formulario OAuth2):

```json
{ "email": "maria.perez@example.com", "password": "Tayrona2026" }
```

`200 OK`:

```json
{
  "access_token": "<JWT RS256>",
  "token_type": "bearer",
  "expires_in": 900,
  "usuario": { "id": "…", "email": "…", "nombre_completo": "…", "rol": "Turista", "email_verificado": false, "creado_en": "…" }
}
```

| HTTP | `code` | Causa |
|---|---|---|
| 401 | `CREDENCIALES_INVALIDAS` | Correo inexistente o mal formado, o contraseña incorrecta: siempre el mismo cuerpo, con `WWW-Authenticate: Bearer` |
| 403 | `CUENTA_INACTIVA` | Credenciales correctas pero la cuenta está desactivada |
| 422 | `VALIDACION` | Falta `email` o `password` |

El token lleva `sub` (id del usuario), `rol`, `jti`, `iat`, `exp`, `iss` (`iam-service`) y `typ` (`access`), y en el encabezado `kid` (huella RFC 7638 de la llave pública). Cada intento queda en la bitácora: `LOGIN_SUCCESS` o `LOGIN_FAIL` con el motivo.

### `POST /api/iam/logout` (UC2)

Requiere `Authorization: Bearer <token>`. Revoca el token (por su `jti`) hasta que expire.

| HTTP | `code` | Causa |
|---|---|---|
| 204 | — | Sesión cerrada, sin cuerpo |
| 401 | `TOKEN_INVALIDO` | Sin token, token inválido, expirado o ya revocado (con `WWW-Authenticate: Bearer`) |
| 503 | `SERVICIO_NO_DISPONIBLE` | Valkey no responde |

### `GET /api/iam/.well-known/jwks.json`

Público. Devuelve las llaves públicas (`{"keys": [{"kty", "n", "e", "kid", "use": "sig", "alg": "RS256"}]}`) para que el Gateway y los demás servicios verifiquen los tokens. Responde `200` con `Cache-Control: public, max-age=300`.

Imagen de contenedor (multi-stage):

```bash
docker build -t iam-service:dev .
docker run --env-file .env -p 8001:8001 iam-service:dev
```

Las llaves JWT (`keys/private.pem`, `keys/public.pem`) no se versionan ni se copian en la imagen; se montan en tiempo de ejecución.

## Decisiones y riesgos conocidos

* **Enumeración de cuentas.** El `409` de `POST /register` permite saber si un correo ya está registrado. Se acepta en el prototipo por usabilidad y se mitiga con rate limiting en Traefik (UC32). Alternativa futura: responder siempre `202` y avisar por correo.
* **IP de origen.** La IP que se guarda en la bitácora solo se toma de `X-Forwarded-For` cuando la petición viene de un proxy listado en `FORWARDED_ALLOW_IPS` (uvicorn con `--proxy-headers`). De cualquier otro cliente se ignora el encabezado y se usa la IP de la conexión.
* **Tokens de acceso cortos, sin refresh token.** Los tokens RS256 duran 15 minutos y por ahora no hay refresh token: al vencer, el usuario vuelve a iniciar sesión.
* **Revocación por `jti` en Valkey, falla cerrado.** El logout guarda `iam:revoked:<jti>` con TTL igual al tiempo restante del token. Si Valkey no responde, se devuelve `503`: nunca se asume que un token "no está revocado" sin poder comprobarlo.
* **El login no revela si un correo existe.** Correo inexistente y contraseña incorrecta devuelven el mismo `401` con el mismo cuerpo, y el primero verifica igual contra un hash Argon2 de relleno para que el tiempo de respuesta sea similar.
* **Bitácora inmutable y sin borrado de usuarios.** `bitacora_auditoria` es de solo inserción (trigger + `REVOKE`, RNF-10). Los usuarios se desactivan (`activo = false`), no se borran: la FK con `RESTRICT` desde la bitácora lo impide.
