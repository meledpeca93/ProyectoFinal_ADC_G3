# Requisitos funcionales y de evaluación — Buscaminas
Fuente principal: `docs/referencias/Proyecto-3-ARQ-Buscaminas.docx` (30 páginas). Este resumen se subordina a esa guía. No añadir funcionalidades opcionales a costa del alcance obligatorio.

## Tecnologías obligatorias
Python 3.12, Django 5.2 LTS, Django Templates, HTML, CSS, JS, PostgreSQL 16, Dockerfile, Docker Compose, Linux (p. ej. Ubuntu Server 24.04), Gunicorn, Caddy o Nginx, Git repositorio remoto.

## Juego y niveles
| Nivel | Tablero | Minas | Seguras | Límite | Multiplicador |
|---|---:|---:|---:|---:|---:|
| Fácil | 8×8 | 10 | 54 | 240 s | 1.0 |
| Normal | 10×10 | 18 | 82 | 360 s | 1.5 |
| Difícil | 12×12 | 30 | 114 | 480 s | 2.0 |

- Generar minas **después del primer clic** en el servidor, excluyendo la celda tocada y sus ocho vecinas, incluso en esquina/borde.
- Revelar número de minas adyacentes en las ocho direcciones; en ceros expandir mediante BFS.
- Bandera/desbandera en ocultas; no se requieren banderas para ganar. No descubrir bandera hasta retirarla.
- Victoria: revelar todas las seguras; derrota: descubrir mina; tiempo agotado y abandono: 0 puntos.
- Puntaje solo si GANA: redondear `((800 + 3 × segundos_restantes) × multiplicador)` según criterio acordado con guía. Operación exclusivamente servidor.
- Control táctil: pulsación larga de 500 ms o botón `Modo bandera`; ratón izquierdo para descubrir, derecho para bandera; teclado accesible.
- Estado: EN_CURSO, GANADA, PERDIDA, TIEMPO_AGOTADO, ABANDONADA. Fin bloquea jugadas (HTTP 409). Una activa por usuario. Jugadas duplicadas idempotentes.
- El tiempo oficial vive en servidor. Recarga/abrir nueva pestaña no reinicia. La guía permite hasta dos segundos de tolerancia para jugadas tardías por red.

## Usuarios y pantallas
- Registro con nombre único, correo válido, validadores contraseña Django, login, logout POST, privacidad 404 para partida ajena.
- Inicio, registro/login, instrucciones, selección de dificultad, tablero, resultado, perfil, historial paginado, clasificación por nivel.
- Perfil: partidas jugadas/ganadas/perdidas, porcentaje victorias, máximo puntaje, promedio tiempo por nivel, alias y preferencias música/efectos/silencio.
- Clasificación pública: top 10 de ganadas por dificultad, solo mejor partida por usuario; desempate por menor duración y luego fecha.
- Responsive desde 360 px sin scroll horizontal. Sonidos de acción/errores/cascada/bandera/explosión/alerta/victoria/derrota y música en bucle; volúmenes independientes guardados; audio tras interacción. Licencias en CREDITOS.md.

## Infraestructura y seguridad
Navegador → HTTPS → proxy → Gunicorn/Django → PostgreSQL. Proxy publica 80/443, web interno 8000, db interno 5432 **sin ports**. Redes frontend/backend (backend internal), volúmenes pgdata y static. .env fuera de repo, .env.example incluido; DEBUG=False, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, check --deploy. Contenedores con límites CPU/RAM y aplicación como usuario no root.

## Evaluación y entregables
- Pruebas comunes C01-C17, pruebas específicas B1-B6, ≥10 pruebas automatizadas `manage.py test` y 1000 tableros primer clic seguro.
- Prueba carga moderada desde otro equipo con métricas de `docker stats`, diagnóstico de fallo controlado, actualización sin pérdida de datos, pg_dump y restauración demostrable.
- Evidencias arquitectura Linux/CPU/RAM/disco/redes/volúmenes/procesos, URL HTTPS en red externa.
- Código y commits de integrantes, `Dockerfile`, Compose, proxy, .env.example, requirements.txt, README, CREDITOS, informe PDF ≥15 páginas, presentación ≥10 diapositivas, bitácora IA, defensa en 35 minutos.

## Nota organizativa
Este equipo está definido por el usuario con **8 integrantes**. La guía describe 3–5 por grupo; conservar ocho en esta planificación. La aceptación administrativa de esa excepción corresponde al catedrático, no al agente.
