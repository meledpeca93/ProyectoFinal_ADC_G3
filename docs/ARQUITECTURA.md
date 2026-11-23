# Arquitectura base del proyecto

## Servicios
```text
Navegador (PC/móvil)
       | HTTPS 443
       v
 proxy (Caddy o Nginx) -----> volumen static (solo lectura)
       | red frontend
       v
 web (Gunicorn + Django 5.2, puerto interno 8000)
       | red backend interna
       v
 db (PostgreSQL 16, 5432 interno; volumen pgdata)
```
`proxy` único con puertos públicos. `web` no publica 8000, `db` no publica 5432. La configuración y los secretos vienen de `.env` no versionado. Fijar nombre de proyecto Compose único para no interferir con sistemas Docker del usuario.

## Módulos y propiedad del código
```text
ProyectoFinal_ADC_G3/
├── AGENTS.md
├── config/               # settings/urls/wsgi
├── cuentas/              # Auth, PerfilJugador (Nelsi)
├── juego/                # Partida, Movimiento y motor (Emerson)
│   ├── services/          # minas.py, reglas.py
│   └── templates/juego/   # Inicio, tablero, resultado, niveles
├── estadisticas/         # consultas historial / ranking (Dimas)
├── templates/base.html   # Milton (después de base inicial del integrador)
├── static/css/            # estilos globales y específicos
├── static/js/             # tablero (Ismael), audio (Kenaliz)
├── static/audio/          # recursos con licencia
├── docs/                  # especificaciones y evidencias
├── Dockerfile
├── compose.yaml
├── Caddyfile
├── requirements.txt
├── .env.example
└── README.md
```
La estructura es propuesta inicial: no crear migraciones incompatibles, ni duplicar servicios estadísticos, ni redefinir endpoints sin acordarlo.

## Modelos mínimos
- `User` Django: username único, email, password hash.
- `PerfilJugador`: FK OneToOne User, alias, volumen_musica, volumen_efectos, silenciado.
- `Partida`: UUID PK, usuario FK, dificultad, estado, inicio_servidor, limite_segundos, fin_servidor, duracion_segundos, puntaje, errores, movimientos, estado_juego JSON **privado**, semilla; restricción única parcial para una EN_CURSO/usuario.
- `Movimiento`: partida FK, numero, tipo, datos JSON, creado_en, aceptado; UniqueConstraint(partida, numero).

## Seguridad y concurrencia
Acción autenticada y autorizada contra propietario; `transaction.atomic()` y bloqueo de fila con `select_for_update()` para procesar jugadas; serializar respuesta si `numero` repetido. Nunca exponer `estado_juego.minas` ni semilla salvo reglas explícitas tras finalizar. Validar tipos, rangos, estado, turno, CSRF y plazo. Las queries de ranking/estadísticas calculan desde PostgreSQL.

## Principio decisivo
**Navegador propone, Django decide.** JS anima y refleja DTO público, no genera minas ni define puntuación/resultado.
