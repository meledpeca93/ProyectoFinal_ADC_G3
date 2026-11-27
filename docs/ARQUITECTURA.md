# Arquitectura base del proyecto

## Servicios

El entorno local conecta el navegador en `127.0.0.1:8080` con Caddy (`web:8000`). Caddy reenvía las peticiones dinámicas a Gunicorn y Django en `api:5000` por la red frontend. Django comprueba su salud en su propio `127.0.0.1:8000` y consulta PostgreSQL en `db:5432` por la red backend interna. El despliegue Linux prevé HTTPS mediante el proxy en 80/443.

`web` sirve la aplicación y `db` tiene un mapeo exclusivo de loopback en `127.0.0.1:15432` para DBeaver. Django accede a PostgreSQL por `backend`. Los secretos vienen de `.env` local y Compose usa el nombre `buscaminas_g3`. El [registro de implementación](../Implementacion_realizadas.md) describe los healthchecks y los volúmenes.

## Módulos y propiedad del código

```text
ProyectoFinal_ADC_G3/
├── api/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/               # settings, rutas y WSGI
│   ├── cuentas/              # Auth y PerfilJugador (Nelsi)
│   ├── juego/                # Partida, Movimiento y motor (Emerson)
│   ├── estadisticas/         # Historial y ranking (Dimas)
│   ├── templates/base.html   # Milton
│   └── static/               # CSS, JS del tablero (Ismael), audio (Kenaliz)
├── web/
│   ├── Dockerfile
│   └── Caddyfile
├── db/
│   └── init.sql
├── docs/
├── compose.yaml
├── .env.example
└── README.md
```

Los modelos y contratos se acuerdan por PR con los responsables de cada módulo.

## Modelos mínimos
- `User` Django: username único, email, password hash.
- `PerfilJugador`: FK OneToOne User, alias, volumen_musica, volumen_efectos, silenciado.
- `Partida`: UUID PK, usuario FK, dificultad, estado, inicio_servidor, limite_segundos, fin_servidor, duracion_segundos, puntaje, errores, movimientos, estado_juego JSON **privado**, semilla; restricción única parcial para una EN_CURSO/usuario.
- `Movimiento`: partida FK, numero, tipo, datos JSON, creado_en, aceptado; UniqueConstraint(partida, numero).

## Seguridad y concurrencia
Acción autenticada y autorizada contra propietario; `transaction.atomic()` y bloqueo de fila con `select_for_update()` para procesar jugadas; serializar respuesta si `numero` repetido. Nunca exponer `estado_juego.minas` ni semilla salvo reglas explícitas tras finalizar. Validar tipos, rangos, estado, turno, CSRF y plazo. Las queries de ranking/estadísticas calculan desde PostgreSQL.

## Principio decisivo
**Navegador propone, Django decide.** JS anima y refleja DTO público, no genera minas ni define puntuación/resultado.
