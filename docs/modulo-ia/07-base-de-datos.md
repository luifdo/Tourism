# Base de datos

> Módulo 5 · [Índice](./README.md)

`recommendation_db` tiene una sola tabla, `recomendacion_log` (SRS, modelo de datos):

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | uuid, PK | Identificador del registro. |
| `conversacion_id` | uuid | Sesión del chatbot. |
| `turista_id` | uuid | Viene del encabezado `X-Usuario-Id`. |
| `servicio_id` | uuid | Servicio recomendado (referencia lógica a `catalog_db`; sin llave foránea entre bases). |
| `justificacion` | texto | Motivo mostrado al turista (RNF-08). |
| `herramientas_usadas` | jsonb | Tools que se consultaron. |
| `modelo` | texto | Proveedor y versión del modelo que generó la respuesta. |
| `fecha_generacion` | timestamp | Marca temporal. |

No se guarda el texto de las conversaciones (privacidad, Ley 1581).

En nuestro compose, un script en `docker-entrypoint-initdb.d` crea la base y la tabla la primera vez que se inicia el volumen. Más adelante se puede sustituir por migraciones (Alembic). Cuando el servicio se una al resto, `recommendation_db` deberá agregarse al init SQL de `infra/`, que hoy no la incluye.

---
[← Variables de entorno](./06-variables-entorno.md) · [Simulación y proveedor de IA →](./08-simulacion.md)
