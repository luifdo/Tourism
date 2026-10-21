# Arquitectura local

> Módulo 5 · [Índice](./README.md)

```
                         ┌──────────────────────────────────────────┐
                         │      docker compose (red interna)        │
                         │                                          │
 curl / Postman  ──8005──►  recommendation-service (FastAPI)         │
                         │      │        │          │               │
                         │      │        │          └──► proveedor de IA (externo, después)
                         │      │        └────────────► valkey      │  sesiones (TTL 24 h)
                         │      └─────────────────────► postgres    │  recommendation_db
                         │      │                                    │
                         │      └──► mock-plataforma  (catalog, booking y review simulados)
                         └──────────────────────────────────────────┘
```

* **recommendation-service:** el microservicio. Es lo único que construimos nosotros.
* **postgres:** instancia de PostgreSQL con la base `recommendation_db`. En el proyecto real es una base lógica dentro de la instancia compartida; aquí tenemos una instancia propia para no depender de `infra/`.
* **valkey:** guarda la conversación reciente de cada sesión.
* **mock-plataforma:** un solo contenedor que responde como catalog, booking y review, con datos fijos de Santa Marta.
* **Proveedor de IA:** es un servicio externo y no forma parte del compose. Se conecta al final mediante una interfaz del servicio (ver [Simulación y proveedor de IA](./08-simulacion.md)).

El módulo no usa RabbitMQ: obtiene los datos bajo demanda con sus tools.

---
[← Alcance](./01-alcance.md) · [Stack elegido →](./03-stack.md)
