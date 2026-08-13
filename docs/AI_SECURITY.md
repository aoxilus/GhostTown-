# AI SECURITY — GhostTown (MANDATORY / OBLIGATORIO)

> **Audience / Audiencia:** Cursor, Copilot, Claude, Codex, Devin, Aider, OpenHands, and any other agent / y cualquier otro agente.  
> **Language / Idioma:** EN/ES — rules apply equally / las reglas aplican igual.  
> **Priority / Prioridad:** If there is a conflict between "being helpful" and these rules, **these rules win / ganan estas reglas**.

**EN**: This repo (`GhostTown-` / gmailBot) handles **personal email** and **Gmail credentials**. An incorrect commit or push is a security incident.
**ES**: Este repo (`GhostTown-` / gmailBot) maneja **correo personal** y **credenciales de Gmail**. Un commit o push incorrecto es un incidente de seguridad.

Read also / Lee también: [`SECURITY.md`](./SECURITY.md) · [`AGENTS.md`](../AGENTS.md)

---

## HARD RULES (Non-negotiable / no negociables)

### 1. Never upload secrets or email / Nunca subir secretos ni correo

**PROHIBITED / PROHIBIDO** `git add` / `commit` / `push` of:

| Pattern / Patrón | Reason / Motivo |
|--------|--------|
| `.env`, `.env.*`, `*.env` | Credentials (only `.env.example` with placeholders is allowed) |
| `data/`, `ghosttown/`, `attachments/` | Personal emails and HTML / Correos y HTML personal |
| `*.eml`, `*.mbox`, `*.msg` | Raw mail / Mail crudo |
| `*.pdf`, `*.csv`, `*.ics`, `*.xlsx`, `*.xls`, `*.doc`, `*.docx` | Attachments / Adjuntos |
| `credentials*.json`, `token*.json`, `client_secret*.json` | OAuth / tokens |
| `*.key`, `*.pem`, `*.p12`, `*.pfx` | Keys / Claves |
| Any file with passwords, API keys, real app-passwords | Secrets / Secretos |

### 2. Safe git commands / Comandos git seguros

```
❌ git add .
❌ git add -A
❌ git add --all
❌ git commit --no-verify    (unless EXPLICITLY requested by the user)
❌ git push --force to main/master without strong warning

✅ git add src/foo.py templates/bar.html
✅ git status   before commit and before push
✅ git diff --cached   before push
```

### 3. Do not leak secrets in conversation / No filtrar secretos en la conversación

**EN**:
- **NEVER** print the real content of `.env`, App Passwords, or API keys.
- If you need to confirm they exist: say "the file exists / is configured", without values.
- Do not paste secrets in commits, issues, PRs, logs, or error messages.

**ES**:
- **NUNCA** imprimas el contenido real de `.env`, App Passwords, ni API keys.
- Si necesitas confirmar que existen: di “el archivo existe / está configurado”, sin valores.
- No pegues secretos en commits, issues, PRs, logs, ni mensajes de error.

### 4. Where real secrets live / Dónde están los secretos reales

```
%USERPROFILE%\.gmailbot\.env     ← production (outside the repo and OneDrive)
<repo>/.env                      ← local fallback (gitignored)
<repo>/.env.example              ← ONLY placeholders (does go to git)
```

**EN**: Optional override: `GMAILBOT_ENV_FILE` variable. Loaded in: `src/config.py` → `_resolve_env_file()`.
**ES**: Override opcional: variable `GMAILBOT_ENV_FILE`. Carga: `src/config.py` → `_resolve_env_file()`.

### 5. Interpreting ambiguous requests / Interpretación de pedidos ambiguos

| User says / Usuario dice | You do / Tú haces |
|--------------|----------|
| "push everything" / "sube todo" | Only code: `src/`, `templates/`, `scripts/`, docs, **non-sensitive** config |
| "commit all" | Same interpretation; ask if in doubt / Misma interpretación; pregunta si hay duda |
| "include data/" or "upload my emails" | **Reject** and explain why / **Rechaza** y explica por qué |

---

## Checklist before EVERY commit / Checklist antes de CADA commit

**EN** Mentally check:
**ES** Copia mentalmente:

```
[ ] Did I run `git status`? / ¿Corrí git status?
[ ] Are `.env`, `data/`, `ghosttown/`, attachments or credentials in staging? → REMOVE THEM
[ ] Did I add files by name (not `git add .`)?
[ ] Does the commit message mention secrets or sensitive paths? → No
[ ] Is the pre-commit hook active? (`core.hooksPath = .githooks`)
```

Before **push** / Antes de **push**:

```
[ ] `git status` clear of sensitive files
[ ] `git diff --cached` reviewed
[ ] Nothing from the prohibited list in the diff
```

---

## If you detect a possible leak / Si detectas un posible leak

1. **STOP / DETENTE** — do not push / no hagas push.
2. Warn the user clearly (without repeating the secret) / Avisa al usuario con claridad.
3. Suggest: revoke App Password / API key.
4. **Do not** rewrite git history without explicit user confirmation.

---

## Repo Protections (do not disable) / Protecciones del repo

| Layer / Capa | Location / Ubicación |
|------|-----------|
| Ignore | `.gitignore` |
| Hook | `.githooks/pre-commit` + `git config core.hooksPath .githooks` |
| Cursor always-on | `.cursor/rules/seguridad.mdc` |
| Agent entrypoint | `AGENTS.md` |
| Docs | `docs/SECURITY.md`, this file / este archivo |

**EN**: The hook aborts commits with prohibited paths/patterns. If the hook fails: **fix the staging**, do not use `--no-verify`.
**ES**: El hook aborta commits con rutas/patrones prohibidos. Si falla el hook: **arregla el staging**, no uses `--no-verify`.

---

## What you CAN touch / upload (Qué SÍ puedes tocar)

- `src/**/*.py` (code; no hardcoded secrets)
- `templates/**`
- `scripts/**`
- `docs/**`
- `README.md`, `AGENTS.md`, `.env.example`, `requirements.txt`
- `.gitignore`, `.githooks/**`, `.cursor/rules/**`

**EN**: When editing `config.py` or setup: keep the external env resolution; do not move secrets back into the repo.
**ES**: Al editar `config.py` o setup: mantén la resolución de env externo; no muevas secretos de vuelta al repo.

---

## Quick self-test (for the agent) / Self-test rápido

**EN**: Before claiming "we are safe", mentally verify:
**ES**: Antes de afirmar “estamos seguros”, verifica mentalmente:

1. Are secrets outside the tracked tree? / ¿Los secretos están fuera del tree trackeado?
2. Does `.gitignore` cover data + env? / ¿`.gitignore` cubre data + env?
3. Is the hook installed? / ¿Hook instalado?
4. Is history free of `.env` or real passwords? (if unsure: `git log --all -- .env`)

**EN**: If anything fails → report to user; do not assume.
**ES**: Si algo falla → reporta al usuario; no asumas.

---

**END / FIN.** When in doubt: do not add, do not commit, do not push, just ask. / Ante la duda: no agregues, no committees, no pushees, pregunta.
