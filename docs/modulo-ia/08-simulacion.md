# Simulación y proveedor de IA

> Módulo 5 · [Índice](./README.md)

## Proveedor de IA

El servicio no está atado a un proveedor. El caso de uso del chat depende de una interfaz (puerto), por ejemplo `ModeloDeLenguaje`, que recibe el mensaje, el historial y la lista de tools, y devuelve la respuesta o la solicitud de una tool. Cada proveedor (Gemini, u otro) es un adaptador en `src/infrastructure/llm/` que implementa esa interfaz.

* **Ahora:** no se conecta ninguno. El equipo proporcionará el proveedor y la clave cuando haga falta. No se construye un proveedor falso.
* **Después:** se escribe el adaptador del proveedor elegido. Cambiar o agregar otro es escribir un adaptador nuevo y elegirlo con `LLM_PROVIDER`; el dominio y los casos de uso no se tocan.
* **Nota:** el SRS y el ADR-010 definen Gemini como el proveedor del proyecto. Esta interfaz no los contradice: Gemini sería el primer adaptador, y si el equipo decide usar otros, convendría actualizar esos documentos.

## Catalog, booking y review

Se simulan sin cambiar el código del servicio. Un único contenedor `mock-plataforma` responde las rutas que usan las tools, con datos fijos:
* **Booking:** `GET /disponibilidad` y `GET /mis-reservas`, tal como están en [`contracts/openapi/booking.yaml`](../../contracts/openapi/booking.yaml).
* **Catalog y review:** sus contratos todavía no existen en `contracts/openapi/`. Hasta que se escriban, el mock define las rutas que usarán las tools (búsqueda y detalle, capacidad de carga, alertas, reseñas). Esas rutas hay que acordarlas con @luifdo.

Para cambiar al servicio real basta apuntar `CATALOG_URL`, `BOOKING_URL` y `REVIEW_URL` a donde estén.

---
[← Base de datos](./07-base-de-datos.md) · [Levantar, probar y verificar →](./09-levantar-y-probar.md)
