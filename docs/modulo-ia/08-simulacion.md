# Simulación y proveedor de IA

> Módulo 5 · [Índice](./README.md)

## Proveedor de IA

El servicio no está atado a un proveedor. El caso de uso del chat depende de una interfaz (puerto), por ejemplo `ModeloDeLenguaje`, que recibe el mensaje, el historial y la lista de tools, y devuelve la respuesta o la solicitud de una tool. Cada proveedor (Gemini, u otro) es un adaptador en `src/infrastructure/llm/` que implementa esa interfaz.

* **Ahora:** no se conecta ninguno. El equipo proporcionará el proveedor y la clave cuando haga falta. No se construye un proveedor falso.
* **Después:** se escribe el adaptador del proveedor elegido. Cambiar o agregar otro es escribir un adaptador nuevo y elegirlo con `LLM_PROVIDER`; el dominio y los casos de uso no se tocan.
* **Nota:** el SRS y el ADR-010 definen Gemini como el proveedor del proyecto. Esta interfaz no los contradice: Gemini sería el primer adaptador, y si el equipo decide usar otros, convendría actualizar esos documentos.

## Catalog, booking y review

Se simulan sin cambiar el código del servicio. Un único contenedor `mock-plataforma` (puerto 9000) responde las rutas que usan las tools, con datos fijos de Santa Marta. Las rutas salen de los contratos de cada servicio:

| Tool | Ruta | Contrato |
|---|---|---|
| `buscar_servicios` | `GET /api/catalog/buscar` (filtros: `texto`, `categoria`, `zona`, `precio_min`, `precio_max`, `lat`, `lon`, `radio_m`, `tipo`, `fecha`, `personas`, entre otros) | `catalog.yaml` |
| `detalle_servicio` | `GET /api/catalog/servicios/{servicio_id}` | `catalog.yaml` |
| `presion_capacidad_carga` | `GET /api/catalog/analitica/capacidad?zona=&fecha=` | `catalog.yaml` |
| `alertas_oficiales` | `GET /api/catalog/alertas?zona=&servicio_id=` | `catalog.yaml` |
| `consultar_disponibilidad` | `GET /api/bookings/disponibilidad?servicio_id=&desde=&hasta=` | [`booking.yaml`](../../contracts/openapi/booking.yaml) |
| `historial_turista` | `GET /api/bookings/mis-reservas` | [`booking.yaml`](../../contracts/openapi/booking.yaml) |
| `resenas_servicio` | `GET /api/reviews/servicios/{servicio_id}/resenas` y `/resumen` | `review.yaml` |

> `catalog.yaml` y `review.yaml` están en las ramas `feature/catalog-service` y `feature/review-service`, todavía no en `develop`. Ya definen todo lo anterior, así que el mock no inventa rutas. Cuando lleguen a `develop`, estos enlaces apuntarán a `contracts/openapi/`. Ojo: el Plan §4.1 dice `GET /api/reviews/servicios/{id}`, pero el contrato real de review usa `/resenas` y `/resumen`.

El mock debe respetar también estas reglas de los contratos:
* **Idioma:** catalog y review responden según `Accept-Language`; las tools lo reenvían.
* **Identidad:** `historial_turista` y `presion_capacidad_carga` reenvían el `X-Usuario-Id` del turista. Para `Turista`, la capacidad devuelve solo `zona`, `fecha`, `nivel` (`BAJO`, `MEDIO`, `ALTO`) y su etiqueta, sin cifras.
* **Errores:** formato común `{error, message, correlation_id}`.

Qué pide catalog al Módulo 5 (su documento de coordinación, sección 8):
* Usar `aviso_pagos.mensaje` de la ficha para avisar al turista que lleve efectivo o que no hay señal.
* Etiquetar los pods con `app.kubernetes.io/name: recommendation-service` en el namespace `turismo-app`; catalog solo acepta llamadas internas de pods con esa etiqueta.

Para cambiar al servicio real basta apuntar `CATALOG_URL`, `BOOKING_URL` y `REVIEW_URL` a donde estén.

---
[← Base de datos](./07-base-de-datos.md) · [Levantar, probar y verificar →](./09-levantar-y-probar.md)
