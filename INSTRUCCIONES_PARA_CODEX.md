# Cómo activar el contexto del proyecto en Codex (VS Code)

1. Descarga y descomprime el ZIP de contexto. Copia **el contenido** de la carpeta `Buscaminas_Contexto_Codex_G3/` a la raíz del clon `ProyectoFinal_ADC_G3/` en VS Code, sin sustituir archivos de aplicación existentes.
2. Deben quedar rutas como `ProyectoFinal_ADC_G3/AGENTS.md` y `ProyectoFinal_ADC_G3/docs/REQUISITOS.md`.
3. Abre la pestaña Codex de VS Code, elige `Work locally` con el repositorio abierto.
4. Copia este mensaje al chat del agente:

> Estoy continuando el proyecto Buscaminas de Arquitectura de Computadoras del Grupo 3 con **ocho integrantes**. Lee primero `AGENTS.md`, `docs/REQUISITOS.md`, `docs/ARQUITECTURA.md`, `docs/CONTRATOS_API.md`, `docs/DISTRIBUCION_EQUIPO.md`, `docs/PLAN_INTEGRACION.md` y revisa las imágenes `docs/diseno/`. Después inspecciona `git status` y la estructura del repositorio. Dame un plan concreto para la v0.1.0 base compartida (Python 3.12, Django 5.2, PostgreSQL 16, Compose) sin modificar archivos todavía. No toques otros proyectos o contenedores Docker.

5. Tras aprobar el plan, autoriza al agente a construir por etapas y verificar con pruebas. Usa commits/PRs por integrante.

**Límite:** esto transfiere el contexto técnico, no importa los mensajes originales ni convierte esta conversación de ChatGPT en una sesión del historial de Codex.
