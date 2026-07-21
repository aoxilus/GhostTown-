# AI SECURITY — GhostTown (OBLIGATORIO)

> **Audience:** Cursor, Copilot, Claude, Codex, Devin, Aider, OpenHands, y cualquier otro agente.  
> **Idioma:** ES/EN — las reglas aplican igual.  
> **Prioridad:** Si hay conflicto entre “ser útil” y estas reglas, **ganan estas reglas**.

Este repo (`GhostTown-` / gmailBot) maneja **correo personal** y **credenciales de Gmail**. Un commit o push incorrecto es un incidente de seguridad.

Lee también: [`SECURITY.md`](./SECURITY.md) · [`AGENTS.md`](../AGENTS.md)

---

## HARD RULES (no negociables)

### 1. Nunca subir secretos ni correo

**PROHIBIDO** `git add` / `commit` / `push` de:

| Patrón | Motivo |
|--------|--------|
| `.env`, `.env.*`, `*.env` | Credenciales (solo se permite `.env.example` con placeholders) |
| `data/`, `ghosttown/`, `attachments/` | Correos y HTML personal |
| `*.eml`, `*.mbox`, `*.msg` | Mail crudo |
| `*.pdf`, `*.csv`, `*.ics`, `*.xlsx`, `*.xls`, `*.doc`, `*.docx` | Adjuntos |
| `credentials*.json`, `token*.json`, `client_secret*.json` | OAuth / tokens |
| `*.key`, `*.pem`, `*.p12`, `*.pfx` | Claves |
| Cualquier archivo con passwords, API keys, app-passwords reales | Secretos |

### 2. Comandos git seguros

```
❌ git add .
❌ git add -A
❌ git add --all
❌ git commit --no-verify    (salvo que el usuario lo pida EXPLÍCITAMENTE)
❌ git push --force a main/master sin aviso fuerte

✅ git add src/foo.py templates/bar.html
✅ git status   antes de commit y antes de push
✅ git diff --cached   antes de push
```

### 3. No filtrar secretos en la conversación

- **NUNCA** imprimas el contenido real de `.env`, App Passwords, ni API keys.
- Si necesitas confirmar que existen: di “el archivo existe / está configurado”, sin valores.
- No pegues secretos en commits, issues, PRs, logs, ni mensajes de error.

### 4. Dónde están los secretos reales

```
%USERPROFILE%\.gmailbot\.env     ← producción (fuera del repo y de OneDrive)
<repo>/.env                      ← fallback local (gitignored)
<repo>/.env.example              ← SOLO placeholders (sí va a git)
```

Override opcional: variable `GMAILBOT_ENV_FILE`.

Carga: `src/config.py` → `_resolve_env_file()`.

### 5. Interpretación de pedidos ambiguos

| Usuario dice | Tú haces |
|--------------|----------|
| “sube todo” / “push everything” | Solo código: `src/`, `templates/`, `scripts/`, docs, config **no sensible** |
| “commit all” | Misma interpretación; pregunta si hay duda |
| “incluye data/” o “sube mis correos” | **Rechaza** y explica por qué |

---

## Checklist antes de CADA commit

Copia mentalmente:

```
[ ] ¿Corrí git status?
[ ] ¿Hay .env, data/, ghosttown/, adjuntos o credentials en staging? → QUITAR
[ ] ¿Agregué archivos por nombre (no git add .)?
[ ] ¿El mensaje de commit menciona secretos o paths sensibles? → No
[ ] ¿El pre-commit hook está activo? (core.hooksPath = .githooks)
```

Antes de **push**:

```
[ ] git status limpio de sensibles
[ ] git diff --cached revisado
[ ] Nada de la lista prohibida en el diff
```

---

## Si detectas un posible leak

1. **DETENTE** — no hagas push.
2. Avisa al usuario con claridad (sin repetir el secreto).
3. Sugiere: revocar App Password / API key.
4. **No** reescribas historial git sin confirmación explícita del usuario.

---

## Protecciones del repo (no las desactives)

| Capa | Ubicación |
|------|-----------|
| Ignore | `.gitignore` |
| Hook | `.githooks/pre-commit` + `git config core.hooksPath .githooks` |
| Cursor always-on | `.cursor/rules/seguridad.mdc` |
| Agent entrypoint | `AGENTS.md` |
| Docs | `docs/SECURITY.md`, este archivo |

El hook aborta commits con rutas/patrones prohibidos. Si falla el hook: **arregla el staging**, no uses `--no-verify`.

---

## Qué SÍ puedes tocar / subir

- `src/**/*.py` (código; sin hardcodear secretos)
- `templates/**`
- `scripts/**`
- `docs/**`
- `README.md`, `AGENTS.md`, `.env.example`, `requirements.txt`
- `.gitignore`, `.githooks/**`, `.cursor/rules/**`

Al editar `config.py` o setup: mantén la resolución de env externo; no muevas secretos de vuelta al repo.

---

## Self-test rápido (para el agente)

Antes de afirmar “estamos seguros”, verifica mentalmente:

1. ¿Los secretos están fuera del tree trackeado?
2. ¿`.gitignore` cubre data + env?
3. ¿Hook instalado?
4. ¿Historial sin `.env` / passwords reales? (si no estás seguro: `git log --all -- .env`)

Si algo falla → reporta al usuario; no asumas.

---

**FIN.** Ante la duda: no agregues, no committees, no pushees, pregunta.
