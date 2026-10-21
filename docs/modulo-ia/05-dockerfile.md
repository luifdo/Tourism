# Dockerfile (explicado)

> Módulo 5 · [Índice](./README.md)

Un `Dockerfile` es la receta para construir la **imagen** del servicio. Una imagen es un paquete con el sistema, Python, nuestro código y sus dependencias. Un **contenedor** es esa imagen en ejecución.

```dockerfile
FROM python:3.12-slim
```
Punto de partida: una imagen oficial con Python 3.12 y un Linux mínimo (`slim`). Lo exige el Plan §7.4.

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
```
Evita crear archivos `.pyc` y hace que los logs salgan al instante en la consola.

```dockerfile
WORKDIR /app
```
Carpeta de trabajo dentro del contenedor. Los comandos siguientes se ejecutan ahí.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
Primero se copia solo la lista de dependencias y se instalan. Se hace antes de copiar el código para que Docker reutilice esta capa mientras `requirements.txt` no cambie, y las reconstrucciones sean rápidas.

```dockerfile
COPY src ./src
```
Ahora sí se copia el código del servicio.

```dockerfile
RUN useradd --create-home appuser
USER appuser
```
Crea un usuario sin privilegios y ejecuta el servicio con él, no como administrador. Es un requisito del Plan §7.4.

```dockerfile
EXPOSE 8005
```
Documenta que el servicio escucha en el puerto 8005. No lo publica por sí solo; eso lo hace el compose.

```dockerfile
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]
```
Comando de arranque. `0.0.0.0` hace que escuche dentro del contenedor y no solo en su interfaz local.

También se agrega un archivo `.dockerignore` para no meter en la imagen `.env`, `.git`, `tests/` ni `__pycache__`.

---
[← Estructura de carpetas](./04-estructura.md) · [Variables de entorno →](./06-variables-entorno.md)
