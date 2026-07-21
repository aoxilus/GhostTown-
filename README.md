# 👻 GhostTown

**EN:** Local Gmail backup that looks like Gmail — but lives on your PC. Free up Gmail / Drive space without losing your mail.  
**ES:** Copia local de Gmail con layout tipo Gmail — pero vive en tu PC. Libera espacio en Gmail / Drive sin perder tu correo.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-local-lightgrey.svg)](#)
[![Platform](https://img.shields.io/badge/Windows-PowerShell-0078D4.svg)](#)

---

## 📚 Docs

| Doc | |
|-----|--|
| [docs/VISION.md](docs/VISION.md) | Idea del proyecto |
| [docs/UI.md](docs/UI.md) | Stats, carpetas, 250/página |
| [docs/SECURITY.md](docs/SECURITY.md) | Secretos y protecciones |

---

## 💡 Idea / The idea

| English | Español |
|--------|---------|
| Your Gmail fills up with years of spam, newsletters, receipts, and real conversations. Deleting blindly is scary. | Tu Gmail se llena de años de spam, newsletters, recibos y conversaciones reales. Borrar a ciegas da miedo. |
| **GhostTown** downloads your mail to your computer as a browsable archive (HTML). Then you can clean Gmail — or empty it — because the copy is already safe on disk. | **GhostTown** baja tu correo a la PC como un archivo navegable (HTML). Luego puedes limpiar Gmail — o vaciarlo — porque la copia ya está segura en disco. |
| Goal: **backup Gmail → free Drive / mailbox space → keep reading everything offline.** | Meta: **respaldar Gmail → liberar espacio en Drive / bandeja → seguir leyendo todo offline.** |

```
Gmail (IMAP)  ──sync──►  Your PC (data/)  ──build──►  GhostTown UI (localhost)
                                                      looks like Gmail, read-only
```

---

## ✨ Features / Características

| 🇬🇧 | 🇪🇸 |
|----|----|
| 📥 IMAP sync (Gmail App Password) | 📥 Sync por IMAP (App Password de Gmail) |
| 🖥️ Gmail-like inbox on `http://127.0.0.1:8765` | 🖥️ Bandeja tipo Gmail en `http://127.0.0.1:8765` |
| 📎 Attachments saved on disk | 📎 Adjuntos guardados en disco |
| 🔍 Search + folder filters | 🔍 Búsqueda + filtros por carpeta |
| 🧙 Setup wizard in the browser if credentials are missing | 🧙 Asistente web si faltan credenciales |
| 🪟 Windows GUI launcher (`GhostTown.bat`) | 🪟 Lanzador GUI en Windows (`GhostTown.bat`) |
| 🤖 Optional AI cleanup (`gpt-4.1-mini`) — confirm before trash | 🤖 Limpieza IA opcional (`gpt-4.1-mini`) — confirmas antes de borrar |
| 🔒 Secrets outside the repo (`%USERPROFILE%\.gmailbot\.env`) | 🔒 Secretos fuera del repo (`%USERPROFILE%\.gmailbot\.env`) |

> **Read-only archive first.** The AI never deletes without your confirmation.  
> **Primero el archivo de solo lectura.** La IA no borra nada sin tu confirmación.

---

## 🚀 Quick start / Inicio rápido

### Windows (easiest / lo más fácil)

1. Install **Python 3.11+** from [python.org](https://www.python.org/downloads/) (check *Add to PATH*).
2. Double-click **`GhostTown.bat`**.
3. Enter your Gmail + App Password in the window (or in the browser wizard).
4. Browse your mail at **http://127.0.0.1:8765**

### CLI

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Credentials: copy .env.example → %USERPROFILE%\.gmailbot\.env  (recommended)
# or → .env in this folder (gitignored)

python -m src.cli verify
python -m src.cli sync --limit 50   # test with 50 messages
python -m src.cli serve             # open UI
```

| Command | What it does / Qué hace |
|---------|-------------------------|
| `python -m src.cli verify` | Test IMAP login / Probar login IMAP |
| `python -m src.cli sync` | Download mail / Bajar correo |
| `python -m src.cli build` | Rebuild HTML / Regenerar HTML |
| `python -m src.cli serve` | Start local UI + API / Arrancar UI local |

Drop `--limit` to sync **everything**.  
Quita `--limit` para bajar **todo**.

---

## 🔑 Gmail App Password (required / obligatorio)

Google does **not** allow your normal password for IMAP. You need a 16-character **App Password**.

Google **no** deja usar tu contraseña normal en IMAP. Necesitas un **App Password** de 16 letras.

1. Use a **personal** Gmail (school/work accounts often block this).  
   Usa Gmail **personal** (las escolares/empresa suelen bloquearlo).
2. Turn on [2-Step Verification](https://myaccount.google.com/security).  
   Activa la [Verificación en 2 pasos](https://myaccount.google.com/security).
3. In Gmail → Settings → Forwarding and POP/IMAP → **Enable IMAP**.  
   Gmail → Configuración → Reenvío y POP/IMAP → **Habilitar IMAP**.
4. Create one at [App Passwords](https://myaccount.google.com/apppasswords) — name it `GhostTown`.  
   Créalo en [App Passwords](https://myaccount.google.com/apppasswords) — nombre: `GhostTown`.
5. Paste the 16 letters into the GUI / wizard / `.env` as `IMAP_PASSWORD` (spaces OK).  
   Pega las 16 letras en el GUI / asistente / `.env` como `IMAP_PASSWORD` (espacios OK).

> If you see *"The setting you are looking for is not available"* → 2FA is off, or you're on a managed school/work account.  
> Si dice *"The setting you are looking for is not available"* → falta 2FA, o estás en una cuenta escolar/empresa.

---

## 🤖 Optional AI cleanup / Limpieza IA (opcional)

Set `OPENAI_API_KEY` in your env file. Model default: **`gpt-4.1-mini`** (cheap).

In the UI, open **Guardián** and ask things like:
- *"borra newsletters y anuncios"*
- *"what commercial mail do I have from 2023?"*

The AI proposes a trash batch. **You confirm.** Mail moves to Gmail Trash via IMAP.  
La IA propone un lote. **Tú confirmas.** Se mueve a la papelera de Gmail por IMAP.

Without an API key, GhostTown still works as a full local backup.  
Sin API key, GhostTown sigue funcionando como backup local completo.

---

## 🔒 Privacy & security / Privacidad y seguridad

| ✅ Safe / Seguro | ❌ Never on GitHub / Nunca en GitHub |
|------------------|-------------------------------------|
| Code, templates, scripts | `.env`, passwords, API keys |
| `.env.example` (placeholders only) | `data/`, `ghosttown/` (your real mail) |
| Secrets in `%USERPROFILE%\.gmailbot\.env` | Attachments (`.pdf`, `.eml`, …) |

Protections in this repo:
1. Strong `.gitignore`
2. Cursor / agent rules (`AGENTS.md`, `.cursor/rules/seguridad.mdc`)
3. Git **pre-commit hook** that blocks secrets
4. Prod env folder **outside** OneDrive / the repo

**Full docs / Documentación completa:**

- [`docs/SECURITY.md`](docs/SECURITY.md) — humans / mantenedores
- [`docs/AI_SECURITY.md`](docs/AI_SECURITY.md) — **obligatorio para otras AIs**
- [`docs/README.md`](docs/README.md) — índice

**Tip:** If an App Password ever lived inside OneDrive, revoke it and create a new one.  
**Tip:** Si un App Password estuvo en OneDrive, revócalo y crea uno nuevo.

---

## 📁 Project layout / Estructura

```
GhostTown-/
├── GhostTown.bat              # Double-click launcher (Windows)
├── AGENTS.md                  # Short rules for AI agents
├── docs/
│   ├── SECURITY.md            # Security model (humans)
│   └── AI_SECURITY.md         # Hard rules for other AIs
├── scripts/
│   ├── Start-GhostTown.ps1    # GUI: ask passwords → verify → open UI
│   └── setup.ps1
├── src/
│   ├── sync_imap.py           # IMAP download
│   ├── export_html.py         # Build Gmail-like HTML
│   ├── server.py              # Local web UI + setup wizard + AI API
│   ├── ai_clean.py            # Optional cleanup chat
│   └── cli.py
├── templates/                 # UI (index, thread, setup, CSS/JS)
├── .env.example               # Placeholders only
├── data/                      # Local mail cache (gitignored)
└── ghosttown/                 # Generated HTML site (gitignored)
```

---

## 🗺️ Roadmap / Próximos pasos

- [ ] Full mailbox sync UX (progress bar for large inboxes)
- [ ] Better Spanish/English UI toggle
- [ ] Export selected threads to Markdown
- [ ] Safer bulk cleanup presets (newsletters / promos)

---

## 📜 License / Licencia

Personal / educational use. You are responsible for your own Gmail credentials and what you delete.  
Uso personal / educativo. Tú eres responsable de tus credenciales y de lo que borres.
