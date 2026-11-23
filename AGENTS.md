# AGENTS.md — ProyectoFinal_ADC_G3 / Buscaminas

## Misión y contexto
Proyecto 3 de Arquitectura de Computadoras (UTH). Juego Buscaminas web de un jugador, desarrollado con Python 3.12, Django 5.2 LTS, PostgreSQL 16, plantillas HTML/CSS/JavaScript, Gunicorn y Docker Compose (proxy Caddy o Nginx, web, db), desplegado en Linux con HTTPS. Repositorio: https://github.com/meledpeca93/ProyectoFinal_ADC_G3.

**Este equipo trabaja con ocho integrantes**; conservar exactamente los ocho nombres y asignaciones de `docs/DISTRIBUCION_EQUIPO.md`. Melvin es responsable de crear primero la base v0.1.0, la contenerización y la integración; los demás desarrollan en ramas propias. La guía original menciona grupos de 3 a 5, pero la planificación de este equipo contempla ocho: no eliminar integrantes ni redistribuir responsabilidades sin petición del usuario.

## Antes de cambiar código
1. Leer `docs/REQUISITOS.md`, `docs/ARQUITECTURA.md`, `docs/CONTRATOS_API.md`, `docs/DISTRIBUCION_EQUIPO.md` y `docs/PLAN_INTEGRACION.md`.
2. Inspeccionar estructura actual, `git status` y archivos existentes. No sobrescribir código no revisado.
3. Resumir plan, módulos afectados, pruebas y riesgos antes de cambios importantes.
4. Conservar estilo visual **Dark Neon**: azul marino, acentos cian luminosos, tarjetas redondeadas, accesible/responsive. Mockups en `docs/diseno/`. Son REFERENCIAS visuales, no capturas de app funcional.
5. Trabajar en el directorio del repositorio. **Nunca** ejecutar comandos destructivos globales sobre Docker (por ejemplo `docker system prune -a`, `docker volume prune`, `docker compose down -v`) ni alterar otros contenedores/volúmenes/proyectos del usuario.

## Reglas innegociables
- El navegador muestra y anima; **Django valida jugadas, tiempo, resultado y puntaje**. Nunca aceptar minas, semilla privada ni puntaje aportado por el cliente.
- Primera pulsación segura con zona 3×3 libre; minas se generan en el servidor después del primer descubrimiento. Exactamente 10/18/30 minas; BFS para ceros.
- Una partida activa por usuario; jugadas con `numero` de secuencia idempotente; resultado final y puntaje persistidos una sola vez; post-final responde 409.
- Tiempo oficial del servidor, tolerancia de red de hasta 2 segundos como señala el documento; recargar no reinicia el reloj.
- Seguridad: login requerido, privacidad 404 para partidas de otros usuarios, POST con CSRF, logout por POST, secretos fuera de Git, DEBUG=False en producción, PostgreSQL nunca publicado al exterior.
- Código compartido en un único proyecto Django: **no** crear ocho proyectos Django, ocho bases de datos o tablas/modelos duplicados.
- Cambios de contratos, modelos, rutas o estilos globales requieren acuerdo e integración por pull request.
- Mantener `README.md`, `.env.example`, `CREDITOS.md`, pruebas y bitácora de IA.

## Secuencia de trabajo inicial del integrador
1. Inspeccionar repositorio local sin cambiar nada.
2. Crear esqueleto v0.1.0 Django y directorios `config`, `cuentas`, `juego`, `estadisticas`, `templates`, `static`, `docs` siguiendo los contratos acordados. Mantener código placeholder solo cuando no invada trabajo asignado.
3. Configurar PostgreSQL + `Dockerfile` + `compose.yaml` + proxy y healthchecks, nombres aislados para este proyecto.
4. Definir `base.html` temporal con interfaz mínima y puntos de extensión; Milton será dueño del diseño final de esa plantilla.
5. Publicar rama de base después de pruebas; los demás trabajan sobre esa base en ramas por integrante.
6. Solicitar aprobación del usuario antes de acciones remotas o destructivas y antes de publicar cambios de producción.

## Criterios de aceptación
- `docker compose up -d --build` inicia servicios propios y `/salud/` comprueba conexión de la base.
- `python manage.py test` ejecuta pruebas; objetivo final ≥10 tests automáticos y matriz C01-C17 + B1-B6.
- Responsive desde 360 px, teclado/ratón/táctil, sonidos tras interacción, historial, perfil, top 10 por nivel y persistencia.
- README permite reproducir instalación; no se entregan contraseñas ni tokens en commits.

## Documentación
`docs/REQUISITOS.md` especificación funcional; `docs/CONTRATOS_API.md` acuerdo entre motor y frontend; `docs/ARQUITECTURA.md` servicios/modelos; `docs/DISTRIBUCION_EQUIPO.md` dueños; `docs/PLAN_INTEGRACION.md` ramas y fases; `docs/diseno/README.md` índice de maquetas.
