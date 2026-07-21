# AGENTS.md - Instrucciones para agentes de IA

Este proyecto respalda correos de Gmail vía IMAP y usa credenciales sensibles.
Cualquier agente de IA (Cursor, Copilot, Claude, Codex, etc.) DEBE seguir estas reglas.

**Documentación completa:**

- [`docs/AI_SECURITY.md`](docs/AI_SECURITY.md) — reglas obligatorias para AIs (léelo primero)
- [`docs/SECURITY.md`](docs/SECURITY.md) — modelo de amenazas y setup humano
- [`docs/README.md`](docs/README.md) — índice

## Regla #1: Nunca subir secretos ni correos a GitHub

Está TERMINANTEMENTE PROHIBIDO agregar/commitear/pushear:

- `.env`, `.env.*`, `*.env` (solo se permite `.env.example` con placeholders)
- `data/`, `ghosttown/`, `attachments/` (correos y adjuntos reales)
- Adjuntos: `*.pdf`, `*.csv`, `*.ics`, `*.xlsx`, `*.doc*`, `*.eml`, `*.mbox`, `*.msg`
- Cualquier `credentials*.json`, `token*.json`, `*.key`, `*.pem`, API keys o passwords

## Regla #2: Comandos git seguros

- PROHIBIDO `git add .` / `git add -A` / `git add --all`. Agrega archivos por nombre.
- Antes de commit/push: correr `git status` y verificar que no hay nada sensible.
- Si detectas un posible leak: DETENTE, no hagas push, avisa al usuario.

## Regla #3: Manejo de credenciales

- Los secretos reales viven fuera del repo: `%USERPROFILE%\.gmailbot\.env`.
- Nunca imprimas el contenido real de `.env` ni credenciales en ningún lado.
- El repo solo debe tener `.env.example` con valores de ejemplo.

## Protecciones activas

- `.gitignore` bloquea secretos, correos y adjuntos.
- Hay un git pre-commit hook (`.githooks/pre-commit`) que aborta el commit
  si detecta archivos prohibidos o patrones de secretos. No lo desactives.
- Regla Cursor: `.cursor/rules/seguridad.mdc` (alwaysApply).

## Estructura del proyecto

- `src/` - código Python (IMAP sync, limpieza con IA, servidor web)
- `templates/` - frontend HTML/JS/CSS
- `scripts/` - scripts de setup y arranque (PowerShell)
- `docs/` - documentación de seguridad (humanos + AIs)
- `data/`, `ghosttown/` - datos locales generados (NUNCA en git)
