# Dockerfile (explicado)

> Módulo 5 · [Índice](./README.md)

Un `Dockerfile` es la receta para construir la **imagen** del servicio. Una imagen es un paquete con el sistema, Python, nuestro código y sus dependencias. Un **contenedor** es esa imagen en ejecución.

El de `services/recommendation-service/Dockerfile` sigue el de catalog-service y tiene **dos etapas**: la primera instala las dependencias y la segunda arma la imagen final, copiando solo lo necesario. Así la imagen final no lleva `uv` ni herramientas de instalación.

## Etapa 1: instalar dependencias

```dockerfile
FROM python:3.12-slim AS builder
```
Punto de partida: una imagen oficial con Python 3.12 y un Linux mínimo (`slim`). Lo exige el Plan §7.4. `AS builder` le pone nombre a esta etapa.

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /bin/uv
```
Copia el programa `uv` desde su imagen oficial. Solo se usa en esta etapa.

```dockerfile
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv
```
Configura `uv`: compila los `.pyc` al instalar (arranque más rápido), copia los archivos en lugar de enlazarlos y crea el entorno virtual en `/opt/venv`.

```dockerfile
WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
```
Se copian solo `pyproject.toml` y `uv.lock` y se instalan las dependencias. `--frozen` obliga a usar exactamente las versiones del `uv.lock`, y `--no-dev` deja fuera las de pruebas. Se hace antes de copiar el código para que Docker reutilice esta capa mientras el `uv.lock` no cambie, y las reconstrucciones sean rápidas.

## Etapa 2: imagen de ejecución

```dockerfile
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
```
Parte de una imagen limpia. No se crean `.pyc` en ejecución, los logs salen al instante y el entorno virtual copiado de la etapa 1 queda en el `PATH`.

```dockerfile
RUN useradd --create-home --uid 1000 recommendation
```
Crea un usuario sin privilegios para ejecutar el servicio, no como administrador (Plan §7.4).

```dockerfile
RUN python -m compileall -q /usr/local/lib/python3.12
```
La imagen oficial de Python borra los `.pyc` de su biblioteca estándar, y en Kubernetes el sistema de archivos es de solo lectura. Sin este paso, cada arranque recompilaría toda la biblioteca estándar. Es una lección que ya aprendió el equipo de catalog.

```dockerfile
WORKDIR /srv
COPY --from=builder /opt/venv /opt/venv
COPY src ./src
```
Copia el entorno con las dependencias ya instaladas y, al final, el código. El código cambia más seguido que las dependencias, por eso va último.

```dockerfile
USER recommendation
EXPOSE 8005
```
Desde aquí todo corre con el usuario sin privilegios. `EXPOSE` documenta que el servicio escucha en el puerto 8005; no lo publica por sí solo, eso lo hace el compose.

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8005/health')"
```
Docker consulta `/health` cada 30 segundos y marca el contenedor como `healthy` o `unhealthy`. Usa Python porque la imagen `slim` no trae `curl`.

```dockerfile
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]
```
Comando de arranque. `0.0.0.0` hace que escuche desde fuera del contenedor y no solo en su interfaz local.

## `.dockerignore`

Lista lo que no debe entrar al construir la imagen: `.venv/`, cachés, `tests/`, `mocks/` y `.env`. Así la imagen es más liviana y el `.env`, con sus claves, nunca queda dentro.

---
[← Estructura de carpetas](./04-estructura.md) · [Variables de entorno →](./06-variables-entorno.md)
