# Estructura de carpetas

> Módulo 5 · [Índice](./README.md)

Sigue la arquitectura hexagonal de la plantilla del monorepo:

```
services/recommendation-service/
├── Dockerfile
├── docker-compose.yml        # compose propio del servicio
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py               # crea la app FastAPI y conecta los adaptadores
│   ├── domain/               # reglas de negocio puras
│   ├── application/          # casos de uso
│   │   └── ports/            # interfaces: modelo de lenguaje, tools, sesiones, log
│   └── infrastructure/
│       ├── http/             # endpoints (chat, health)
│       ├── persistence/      # PostgreSQL y Valkey
│       ├── llm/              # adaptadores del proveedor de IA (uno por proveedor)
│       └── tools/            # clientes HTTP hacia catalog, booking y review
├── mocks/                    # contenedor mock-plataforma
└── tests/
    ├── unit/
    └── integration/
```

Las carpetas `llm/` y `tools/` son nuevas respecto a la plantilla; la plantilla trae `messaging/`, que este módulo no usa.

---
[← Stack elegido](./03-stack.md) · [Dockerfile (explicado) →](./05-dockerfile.md)
