# Seguridad — GhostTown

Este proyecto sincroniza correo personal de Gmail. Un error de `git add` o un agente de IA puede filtrar **credenciales** y **correos** a GitHub. Esta guía documenta las protecciones activas y cómo mantenerlas.

## Resumen ejecutivo

| Qué | Dónde | ¿Va a GitHub? |
|-----|-------|---------------|
| Código (`src/`, `templates/`, `scripts/`) | Repo | Sí |
| Placeholders (`.env.example`) | Repo | Sí |
| Credenciales reales | `%USERPROFILE%\.gmailbot\.env` | **Nunca** |
| Correos / adjuntos (`data/`, `ghosttown/`) | Disco local (a menudo OneDrive) | **Nunca** |

## Dónde viven los secretos

### Folder de producción (recomendado)

```
%USERPROFILE%\.gmailbot\.env
```

En Windows típico: `C:\Users\<usuario>\.gmailbot\.env`

Ventajas:

- Fuera del repo → git no lo ve
- Fuera de OneDrive → no se sincroniza a la nube de Microsoft por defecto
- `src/config.py` lo carga automáticamente

### Prioridad de carga (`src/config.py`)

1. Variable de entorno `GMAILBOT_ENV_FILE` (ruta explícita)
2. `%USERPROFILE%\.gmailbot\.env`
3. `<repo>/.env` (fallback local; está en `.gitignore`)

### Plantilla pública

Solo `.env.example` con valores falsos. Nunca copies valores reales ahí.

```env
IMAP_HOST=imap.gmail.com
IMAP_USER=tu@gmail.com
IMAP_PASSWORD=xxxx-xxxx-xxxx-xxxx
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
PORT=8765
```

## Capas de protección

### 1. `.gitignore`

Bloquea, entre otros:

- `.env`, `.env.*` (excepto `.env.example`)
- `data/`, `ghosttown/`, `attachments/`, `secrets/`, `prod/`
- Adjuntos y mail: `*.eml`, `*.mbox`, `*.pdf`, `*.csv`, `*.ics`, `*.xlsx`, …
- Credenciales OAuth: `credentials*.json`, `token*.json`, `*.key`, `*.pem`

### 2. Reglas para agentes de IA

| Archivo | Uso |
|---------|-----|
| [`docs/AI_SECURITY.md`](./AI_SECURITY.md) | Guía completa para cualquier AI |
| [`AGENTS.md`](../AGENTS.md) | Resumen en la raíz (muchos agentes lo leen solos) |
| [`.cursor/rules/seguridad.mdc`](../.cursor/rules/seguridad.mdc) | Siempre activa en Cursor |

### 3. Pre-commit hook

Ruta: `.githooks/pre-commit`  
Activado con: `git config core.hooksPath .githooks`

El hook **aborta el commit** si:

- Hay rutas prohibidas en staging (`.env`, `data/`, `ghosttown/`, adjuntos, etc.)
- El contenido parece API key (`sk-…`), password asignado, o clave privada

**No desactives el hook** (`--no-verify`) salvo emergencia consciente y temporal.

### 4. Política de comandos git

- Prohibido: `git add .` / `git add -A` / `git add --all`
- Solo: `git add ruta/archivo.ext` archivo por archivo
- Antes de commit/push: `git status` y revisar staging

## Qué nunca debe subir a GitHub

```
.env  .env.local  .env.production
data/  ghosttown/  attachments/
*.eml  *.mbox  *.msg  *.pdf  *.csv  *.ics  *.xlsx  *.doc*
credentials*.json  token*.json  client_secret*.json
*.key  *.pem  *.p12  *.pfx
```

Si el usuario dice “sube todo”, significa **solo código fuente**, no datos ni secretos.

## Checklist tras clonar / en máquina nueva

1. Crear carpeta: `mkdir %USERPROFILE%\.gmailbot`
2. Copiar `.env.example` → `%USERPROFILE%\.gmailbot\.env` y rellenar valores reales
3. Activar hooks: `git config core.hooksPath .githooks`
4. Verificar ignore: `git check-ignore -v .env`
5. Probar login: `python -m src.cli verify`

## Rotación de App Password (recomendado)

Si el App Password alguna vez estuvo dentro de una carpeta sincronizada (OneDrive, Dropbox, etc.):

1. Revócalo en [App Passwords](https://myaccount.google.com/apppasswords)
2. Crea uno nuevo
3. Guárdalo **solo** en `%USERPROFILE%\.gmailbot\.env`
4. Borra o vacía cualquier `.env` viejo dentro del repo / OneDrive

## Si sospechas un leak

1. **No hagas push**
2. Revisa: `git log --all --full-history -- .env data/ ghosttown/`
3. Busca el secreto en el historial (sin pegarlo en chats públicos)
4. Revoca App Password / API key de inmediato
5. Solo reescribe historial (`git filter-repo`, BFG, etc.) con confirmación explícita del dueño del repo

## Relacionado

- [AI_SECURITY.md](./AI_SECURITY.md) — reglas obligatorias para agentes
- [README.md](../README.md) — sección Privacy & security
