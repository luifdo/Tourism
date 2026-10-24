# Levantar, probar y verificar

> Módulo 5 · [Índice](./README.md)

Requisito: Docker y Docker Compose instalados, y tu usuario en el grupo `docker` (si `docker ps` da "permission denied", cierra sesión y vuelve a entrar).

```bash
cd services/recommendation-service
cp .env.example .env
docker compose up --build -d   # construye la imagen y levanta el servicio
docker compose logs -f         # ver los logs (Ctrl+C para salir)
docker compose down            # apaga los contenedores
```

Por ahora el compose levanta solo el servicio. PostgreSQL y Valkey se agregan en la Fase 1 y el mock de la plataforma en la Fase 2; con ellos, `docker compose down -v` también borrará los datos.

## Verificación (Fase 0)

| Comprobación | Comando | Resultado esperado |
|---|---|---|
| Servicio vivo | `curl localhost:8005/health` | `{"status":"ok"}` con código 200 |
| Métricas | `curl localhost:8005/metrics` | Texto en formato Prometheus |
| Estado | `docker compose ps` | `Up ... (healthy)` |
| Usuario | `docker compose exec recommendation-service id` | `uid=1000(recommendation)`, sin privilegios |

Verificaciones de fases posteriores:

| Comprobación | Comando | Resultado esperado |
|---|---|---|
| Chat (Fase 3) | `curl -X POST localhost:8005/api/recommendations/chat -H "X-Usuario-Id: <uuid>" -H "Content-Type: application/json" -d '{"mensaje":"¿Qué puedo hacer en Taganga?"}'` | Respuesta con recomendaciones justificadas |
| Registro (Fase 1) | Consultar `recomendacion_log` en PostgreSQL | Una fila por recomendación |
| Sesión (Fase 1) | Segunda consulta con el mismo `conversacion_id` | El servicio recuerda el contexto |

## Pruebas y calidad

Con `uv` (desde `services/recommendation-service/`):

```bash
uv sync                  # instala las dependencias, incluidas las de desarrollo
uv run pytest --cov      # pruebas con cobertura (mínimo 70 %)
uv run ruff check .      # revisión de estilo
```

`pytest` cubre las pruebas unitarias (dominio y casos de uso con los puertos simulados), la de contrato y, desde la Fase 1, las de integración (PostgreSQL y Valkey reales).

La prueba de contrato (`tests/unit/test_contrato.py`) comprueba que el código no exponga ninguna ruta que `contracts/openapi/recommendation.yaml` no declare. El contrato manda: se cambia primero, y el código lo sigue.

---
[← Simulación y proveedor de IA](./08-simulacion.md) · [Plan por fases →](./10-plan-por-fases.md)
