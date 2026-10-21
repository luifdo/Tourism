# Levantar, probar y verificar

> Módulo 5 · [Índice](./README.md)

Requisito: Docker y Docker Compose instalados.

```bash
cd services/recommendation-service
cp .env.example .env
docker compose up --build      # construye la imagen y levanta todo
docker compose down            # apaga los contenedores
docker compose down -v         # además borra los datos (reinicia la base)
```

Verificación:

| Comprobación | Comando | Resultado esperado |
|---|---|---|
| Servicio vivo | `curl localhost:8005/health` | `200` |
| Métricas | `curl localhost:8005/metrics` | Texto en formato Prometheus |
| Chat | `curl -X POST localhost:8005/api/recommendations/chat -H "X-Usuario-Id: <uuid>" -H "Content-Type: application/json" -d '{"mensaje":"¿Qué puedo hacer en Taganga?"}'` | Respuesta con recomendaciones justificadas |
| Registro | Consultar `recomendacion_log` en PostgreSQL | Una fila por recomendación |
| Sesión | Segunda consulta con el mismo `conversacion_id` | El servicio recuerda el contexto |

Pruebas: `pytest` para unitarias (dominio y casos de uso con los puertos simulados) y de integración (PostgreSQL y Valkey reales).

> El cuerpo exacto de la petición del chat se fija en `contracts/openapi/recommendation.yaml`, que se escribe antes del código.

---
[← Simulación y proveedor de IA](./08-simulacion.md) · [Plan por fases →](./10-plan-por-fases.md)
