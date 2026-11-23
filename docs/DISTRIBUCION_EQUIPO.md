# Equipo de desarrollo — 8 integrantes (mantener los ocho)

| Nº | Integrante | Cuenta | Módulo propietario | Entrega clave |
|---:|---|---|---|---|
| 1 | Milton Javier Mejía Bardales | 202410011134 | UI global, Inicio y Resultado | `templates/base.html`, CSS base, inicio y variantes de resultado |
| 2 | Nelsi Johana García Cerín | 202310030084 | Registro, login y perfil | App `cuentas`, `PerfilJugador`, formularios, preferencias persistidas |
| 3 | Emerson Ariel Midence | 202010110222 | Motor y API autoritativa | `Partida`, `Movimiento`, generación, BFS, validaciones, endpoints |
| 4 | Ismael Edgardo Funez | 202010010108 | Tablero jugable | Cuadrícula responsive, JS fetch/CSRF, controles ratón/táctil/teclado |
| 5 | Dimas Hernández | 202410110004 | Historial y clasificación | Consultas ORM, pantallas, paginación, estadísticas y top 10 |
| 6 | Kenaliz Ayeska Chávez Servellón | 202410010301 | Instrucciones, niveles y audio | Cómo jugar, selección dificultad, música/efectos/preferencias |
| 7 | Edith Palencia | 202230120024 | Calidad y documentación | ≥10 tests, C01–C17/B1–B6, evidencias, informe y presentación |
| 8 | Melvin Edgardo Peña Caballero | 201230010100 | Base v0.1.0, Docker, Linux e integración | Esqueleto común, Compose proxy/web/db, CI de integración, despliegue, backup |

**Principio de equidad:** un módulo no se mide por número de pantallas sino complejidad: motor y DevOps requieren menos pantallas pero más pruebas/operación. Los ocho deben entregar commits, evidencias y defender el proyecto completo.

## Referencias visuales
Ver `docs/diseno/README.md`, que relaciona cada mockup con responsables. Las imágenes NO constituyen código listo para usar.

## Entregables mínimos por responsable
1. **Milton:** inicio, resultado para cuatro desenlaces, layout responsive 360 px, CSS reutilizable y componentes.
2. **Nelsi:** registro, login/logout POST, validación y privacidad, edición perfil, preferencias música/efectos.
3. **Emerson:** minas primer clic (1000 pruebas), BFS, acciones idempotentes, cierre por tiempo, puntaje y DTO público.
4. **Ismael:** tablero 8/10/12, clic izquierdo/derecho, pulsación larga 500 ms, modo bandera, bloqueo final, reconexión.
5. **Dimas:** historial paginado filtrable, estadísticas sin mezclar usuarios, top 10 por dificultad con desempate.
6. **Kenaliz:** instrucciones y niveles correctos, sonidos y música con licencias, control separado y persistencia.
7. **Edith:** matriz pruebas, automatización, defectos, README, informe ≥15 páginas, diapositivas ≥10 y bitácora IA.
8. **Melvin:** base compartida inicial, Dockerfile usuario no root, Compose aislado, seguridad, URL HTTPS, medición recursos y recuperación PostgreSQL.

Para instrucciones específicas y criterios terminados, consultar `docs/referencias/Informe_Distribucion_Proyecto_Buscaminas_Grupo_8.pdf`.
