# Buscaminas · Grupo 3

Base v0.1.0 de Arquitectura de Computadoras. El entorno local usa Docker Engine, Docker Compose v2 y un único archivo `compose.yaml`.

- `api/` contiene el Dockerfile, el proyecto Django, sus aplicaciones, plantillas y archivos estáticos.
- `web/` contiene el Dockerfile y la configuración de Caddy.
- `db/` contiene el SQL de inicialización de PostgreSQL.

## Arranque local

1. Copia `.env.example` a `.env`. Completa `POSTGRES_PASSWORD` y `DJANGO_SECRET_KEY` con valores distintos y aleatorios. Puedes generar cada uno con `openssl rand -hex 32`.
2. Comprueba que el puerto local 8080 esté libre. Si está ocupado, define otro `WEB_PORT` en `.env` y usa ese puerto en los pasos siguientes.
3. Ejecuta estos comandos desde la raíz del repositorio.

   ```sh
   docker compose config --quiet
   docker compose up -d --build
   docker compose ps
   curl -fsS http://127.0.0.1:8080/salud/
   docker compose exec api python manage.py test
   ```

Abre <http://127.0.0.1:8080/> para ver la página provisional. La comprobación de salud devuelve `{"estado": "ok"}` cuando Django puede consultar PostgreSQL. Compose espera la salud de la base antes de iniciar Django y la de Django antes de iniciar Caddy.

Para detener y retirar los contenedores del proyecto, ejecuta `docker compose down`. Conserva los volúmenes al detener el entorno. Consulta el [registro de implementación](Implementacion_realizadas.md) para ver la arquitectura, los recursos y el relevo entre colaboradores.
