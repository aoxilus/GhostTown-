# Security — GhostTown (Seguridad)

**EN**: This project synchronizes personal Gmail emails. An accidental `git add` or an AI agent could leak **credentials** and **emails** to GitHub. This guide documents the active protections and how to maintain them.
**ES**: Este proyecto sincroniza correo personal de Gmail. Un error de `git add` o un agente de IA puede filtrar **credenciales** y **correos** a GitHub. Esta guía documenta las protecciones activas y cómo mantenerlas.

## Executive Summary / Resumen ejecutivo

| What / Qué | Where / Dónde | Goes to GitHub? / ¿Va a GitHub? |
|-----|-------|---------------|
| Code / Código (`src/`, `templates/`, `scripts/`) | Repo | Yes / Sí |
| Placeholders (`.env.example`) | Repo | Yes / Sí |
| Real Credentials / Credenciales reales | `%USERPROFILE%\.gmailbot\.env` | **Never / Nunca** |
| Emails & Attachments / Correos y adjuntos (`data/`, `ghosttown/`) | Local disk / Disco local | **Never / Nunca** |

## Where secrets live / Dónde viven los secretos

### Production folder (recommended) / Folder de producción (recomendado)

```
%USERPROFILE%\.gmailbot\.env
```

**EN**: On a typical Windows setup: `C:\Users\<user>\.gmailbot\.env`
**ES**: En Windows típico: `C:\Users\<usuario>\.gmailbot\.env`

**EN** Advantages:
- Outside the repo → git doesn't see it
- Outside OneDrive → doesn't sync to the cloud by default
- `src/config.py` loads it automatically

**ES** Ventajas:
- Fuera del repo → git no lo ve
- Fuera de OneDrive → no se sincroniza a la nube por defecto
- `src/config.py` lo carga automáticamente

### Load Priority / Prioridad de carga (`src/config.py`)

1. Environment variable / Variable de entorno `GMAILBOT_ENV_FILE` (explicit path / ruta explícita)
2. `%USERPROFILE%\.gmailbot\.env`
3. `<repo>/.env` (local fallback; in `.gitignore`)

### Public Template / Plantilla pública

**EN**: Only `.env.example` with fake values. Never copy real values there.
**ES**: Solo `.env.example` con valores falsos. Nunca copies valores reales ahí.

```env
IMAP_HOST=imap.gmail.com
IMAP_USER=your@gmail.com
IMAP_PASSWORD=xxxx-xxxx-xxxx-xxxx
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
PORT=8765
```

## Protection Layers / Capas de protección

### 1. `.gitignore`

**EN**: Blocks, among others:
**ES**: Bloquea, entre otros:

- `.env`, `.env.*` (except `.env.example`)
- `data/`, `ghosttown/`, `attachments/`, `secrets/`, `prod/`
- Attachments & mail / Adjuntos y mail: `*.eml`, `*.mbox`, `*.pdf`, `*.csv`, `*.ics`, `*.xlsx`, …
- OAuth Credentials / Credenciales OAuth: `credentials*.json`, `token*.json`, `*.key`, `*.pem`

### 2. AI Agent Rules / Reglas para agentes de IA

| File / Archivo | Use / Uso |
|---------|-----|
| [`docs/AI_SECURITY.md`](./AI_SECURITY.md) | Full guide for any AI / Guía completa para cualquier AI |
| [`AGENTS.md`](../AGENTS.md) | Summary at root / Resumen en la raíz |
| [`.cursor/rules/seguridad.mdc`](../.cursor/rules/seguridad.mdc) | Always active in Cursor / Siempre activa en Cursor |

### 3. Pre-commit hook

**EN**: Path: `.githooks/pre-commit` | Activated with: `git config core.hooksPath .githooks`
**ES**: Ruta: `.githooks/pre-commit` | Activado con: `git config core.hooksPath .githooks`

**EN**: The hook **aborts the commit** if:
- Prohibited paths are in staging (`.env`, `data/`, `ghosttown/`, attachments, etc.)
- Content looks like an API key (`sk-…`), password, or private key

**ES**: El hook **aborta el commit** si:
- Hay rutas prohibidas en staging (`.env`, `data/`, `ghosttown/`, adjuntos, etc.)
- El contenido parece API key (`sk-…`), password, o clave privada

**EN**: **Do not disable the hook** (`--no-verify`) unless it's a conscious emergency.
**ES**: **No desactives el hook** (`--no-verify`) salvo emergencia consciente.

### 4. Git Command Policy / Política de comandos git

- Prohibited / Prohibido: `git add .` / `git add -A` / `git add --all`
- Only / Solo: `git add path/to/file.ext` (file by file / archivo por archivo)
- Before commit/push / Antes de commit/push: `git status` and review staging / revisar staging

## What should NEVER go to GitHub / Qué nunca debe subir a GitHub

```
.env  .env.local  .env.production
data/  ghosttown/  attachments/
*.eml  *.mbox  *.msg  *.pdf  *.csv  *.ics  *.xlsx  *.doc*
credentials*.json  token*.json  client_secret*.json
*.key  *.pem  *.p12  *.pfx
```

**EN**: If the user says "upload everything", it means **source code only**, not data or secrets.
**ES**: Si el usuario dice "sube todo", significa **solo código fuente**, no datos ni secretos.

## Checklist after cloning / Checklist tras clonar

1. Create folder / Crear carpeta: `mkdir %USERPROFILE%\.gmailbot`
2. Copy / Copiar `.env.example` → `%USERPROFILE%\.gmailbot\.env` and fill with real values / rellenar valores reales
3. Activate hooks / Activar hooks: `git config core.hooksPath .githooks`
4. Verify ignore / Verificar ignore: `git check-ignore -v .env`
5. Test login / Probar login: `python -m src.cli verify`

## App Password Rotation / Rotación de App Password (recommended)

**EN**: If the App Password was ever inside a synced folder (OneDrive, Dropbox, etc.):
**ES**: Si el App Password alguna vez estuvo dentro de una carpeta sincronizada (OneDrive, Dropbox, etc.):

1. Revoke it at / Revócalo en [App Passwords](https://myaccount.google.com/apppasswords)
2. Create a new one / Crea uno nuevo
3. Save it **only** in / Guárdalo **solo** en `%USERPROFILE%\.gmailbot\.env`
4. Delete any old `.env` inside the repo/OneDrive / Borra cualquier `.env` viejo en el repo / OneDrive

## If you suspect a leak / Si sospechas un leak

1. **Do not push / No hagas push**
2. Review / Revisa: `git log --all --full-history -- .env data/ ghosttown/`
3. Search for the secret in history / Busca el secreto en el historial
4. Revoke the App Password/API key immediately / Revoca App Password / API key de inmediato
5. Only rewrite history / Solo reescribe historial (`git filter-repo`, BFG) with explicit owner confirmation / con confirmación explícita del dueño

## Related / Relacionado

- [AI_SECURITY.md](./AI_SECURITY.md) — mandatory rules for agents / reglas obligatorias para agentes
- [README.md](../README.md) — Privacy & security section / sección Privacy & security
