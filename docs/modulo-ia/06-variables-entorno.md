# Variables de entorno

> Módulo 5 · [Índice](./README.md)

El archivo `.env.example` actual trae variables de RabbitMQ que este módulo no usa. Queda así (los valores son de desarrollo; el `.env` real nunca se sube al repositorio):

```
SERVICE_PORT=8005

# Base de datos propia
DB_URL=postgresql+psycopg://turismo:turismo@postgres:5432/recommendation_db

# Sesiones del chat
VALKEY_URL=redis://valkey:6379/0

# Servicios que consultan las tools (en local apuntan al mock)
CATALOG_URL=http://mock-plataforma:9000/api/catalog
BOOKING_URL=http://mock-plataforma:9000/api/bookings
REVIEW_URL=http://mock-plataforma:9000/api/reviews

# Proveedor de IA (se llena cuando se conecte uno; ver 08-simulacion.md)
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
```

Las variables del proveedor de IA son genéricas (`LLM_*`) y quedan vacías hasta que se conecte uno. En Kubernetes la clave será un `Secret` y el modelo un `ConfigMap`.

> El SRS y el Plan nombran `GEMINI_API_KEY` y `GEMINI_MODEL`. Si se usa Gemini como primer proveedor, esos nombres se asignan en su adaptador o se actualizan los documentos del proyecto.

---
[← Dockerfile (explicado)](./05-dockerfile.md) · [Base de datos →](./07-base-de-datos.md)
