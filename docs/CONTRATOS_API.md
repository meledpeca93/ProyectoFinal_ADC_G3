# Contratos de integración (propuesta v0.1; acordar antes de implementación)
El dueño de endpoints/Partida es **Emerson**; frontend del tablero **Ismael**. El integrador es **Melvin**. Campos de ejemplo se deben aprobar en PR antes de fijar una implementación. Prohibido exponer campos privados.

## Rutas mínimas de la guía
| Método | Ruta | Dueño |
|---|---|---|
| GET | `/` | Milton |
| GET, POST | `/cuentas/registro/`, `/cuentas/login/` | Nelsi |
| POST | `/cuentas/logout/` | Nelsi |
| GET | `/instrucciones/`, `/jugar/` | Kenaliz |
| POST | `/partidas/nueva/` | Emerson |
| GET | `/partidas/<uuid>/` | Emerson + Ismael |
| GET | `/api/partidas/<uuid>/estado/` | Emerson |
| POST | `/api/partidas/<uuid>/accion/` | Emerson |
| POST | `/api/partidas/<uuid>/abandonar/` | Emerson |
| GET | `/partidas/<uuid>/resultado/` | Milton |
| GET | `/perfil/` | Nelsi (estadísticas Dimas) |
| GET | `/historial/` | Dimas |
| GET | `/clasificacion/?nivel=facil|normal|dificil` | Dimas |
| GET | `/salud/` | Melvin |

## Contrato JSON sugerido: jugada
`POST /api/partidas/<uuid>/accion/` con sesión Django y CSRF:
```json
{"numero": 7, "tipo": "descubrir", "f": 3, "c": 4}
```
`tipo` = `descubrir` o `bandera`. Coordenadas **base cero** `[f, c]`; `numero` monotónico por partida. Repetición de `numero` devuelve MISMA respuesta, sin volver a aplicar. Tipos incorrectos, coordenadas fuera del tablero y banderas inválidas reciben 400/422 acordado; partida finalizada 409; partida ajena 404.

## DTO público sugerido: estado y respuesta
```json
{
  "partida_id": "<uuid>",
  "estado": "EN_CURSO",
  "dificultad": "normal",
  "filas": 10,
  "columnas": 10,
  "minas_total": 18,
  "banderas": 3,
  "seguras_descubiertas": 37,
  "seguras_total": 82,
  "movimientos": 52,
  "segundos_restantes": 182,
  "tablero": [
    {"f": 0, "c": 0, "estado": "descubierta", "numero": 1},
    {"f": 0, "c": 1, "estado": "oculta"},
    {"f": 0, "c": 2, "estado": "bandera"}
  ],
  "puntaje": null,
  "numero_confirmado": 7
}
```
La lista `tablero` representa todas las casillas visibles o cambios, según se acuerde. En producción, definir **una sola forma** (estado completo recomendado por tamaño reducido) y mantener contrato estable. `numero` solo en descubiertas; nunca serializar `minas` privadas, semilla, solución o valores de celdas ocultas. Tras finalización se pueden revelar minas explícitamente. Puntaje final solo servidor.

## Transiciones
`EN_CURSO` → `GANADA|PERDIDA|TIEMPO_AGOTADO|ABANDONADA`. POST una vez, actualización atómica e idempotente. HTTP 409 para nuevas acciones posteriores al final. Una partida EN_CURSO por usuario; nueva partida requiere confirmación y abandona anterior. Respetar 2 s de tolerancia documentados para latencia.

## Acuerdos entre integrantes
- Milton proporciona layout; otros extienden `base.html`.
- Nelsi publica APIs/servicio de preferencias; Kenaliz consume sin duplicar modelo.
- Emerson es único propietario de motor/Partida/Movimiento y de datos secretos.
- Ismael consume el DTO del servidor y no simula victoria ni tiempo oficial.
- Dimas consulta modelos existentes; no almacena puntajes independientes.
- Edith valida casos C01–C17/B1–B6 y documenta contratos.
- Melvin revisa PRs y compatibilidad de migraciones/Compose.
