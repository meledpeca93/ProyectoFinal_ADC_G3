# Plan de integración del Grupo 3 — ocho desarrolladores

## Regla de inicio
**Melvin** prepara y publica una rama base v0.1.0 primero. Otros siete parten de esa rama cuando haya arranque reproducible. No editar directamente `main` ni duplicar apps y modelos.

## Ramas sugeridas
- `main` — solo código aprobado e integrado.
- `develop` — integración continua del grupo (crear después de base v0.1.0).
- `feature/01-milton-ui`
- `feature/02-nelsi-cuentas`
- `feature/03-emerson-motor`
- `feature/04-ismael-tablero`
- `feature/05-dimas-estadisticas`
- `feature/06-kenaliz-instrucciones-audio`
- `feature/07-edith-calidad-docs`
- `feature/08-melvin-infraestructura`

## Contrato de PR
Cada pull request documenta: dueño, alcance, rutas y modelos modificados, screenshots si UI, pruebas ejecutadas, migraciones nuevas, dependencias entre módulos, y posibles conflictos. Revisión por Melvin + el propietario funcional del módulo afectado. `main` protegido recomendado.

## Hitos verificables
| Hito | Salida | Responsable principal |
|---|---|---|
| H0 | Contexto, estructura, arquitectura y contratos acordados | Melvin + todos |
| H1 | Bocetos y reglas cerradas; base Django v0.1.0 con PG/Compose funcional | Melvin (base), Milton (UI), Emerson (modelo) |
| H2 | Login y motor base; tablero mock conectado; endpoints estabilizados | Nelsi, Emerson, Ismael |
| H3 | Instrucciones, niveles, audio, perfil, resultados, ranking/historial | Milton, Kenaliz, Nelsi, Dimas |
| H4 | Integración y pruebas comunes/específicas, UI desde 360 px | Edith + todos |
| H5 | Deploy Linux, HTTPS, métricas, fallo controlado, backup/restauración | Melvin + Edith |
| H6 | README, informe, presentación y defensa ensayada | Edith + todos |

## Tareas que deben coordinarse especialmente
- Milton y Melvin: `base.html` provisional vs. final. El integrador no debe apropiarse permanentemente del layout.
- Nelsi y Dimas: estadísticas en perfil y nombres ORM.
- Emerson e Ismael: `/api/partidas/.../accion/` + estructura del DTO antes de desarrollar en paralelo.
- Kenaliz y Emerson: niveles son constantes **del servidor**.
- Kenaliz y Nelsi: preferencias de sonido persistentes.
- Todos y Edith: pruebas/evidencias de su módulo, no dejar documentación para el último día.

## Integración segura
Antes de fusionar: `git status`, revisión de migraciones, `docker compose config`, unit tests, check de rutas, test manual. Usar `docker compose -p buscaminas_g3` o `COMPOSE_PROJECT_NAME=buscaminas_g3`, y no mapear puertos de otros proyectos. No usar `down -v` ni `prune` sin orden explícita.

## Primera solicitud que se dará a Codex
Leer `AGENTS.md` y el resto de docs. Inspeccionar repo. Diseñar la estructura base v0.1.0 y **no modificar nada hasta que el usuario revise el plan**.
