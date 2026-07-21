# 👻 GhostTown 🥑

**EN:** Local Gmail backup that looks like Gmail — but lives on your PC. Free up Gmail / Drive space without losing your mail.

**ES:** Copia local de Gmail con layout tipo Gmail — pero vive en tu PC. Libera espacio en Gmail / Drive sin perder tu correo.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Windows-PowerShell-0078D4.svg)](#)
[![Aguacate](https://img.shields.io/badge/%F0%9F%A5%91%20aguacate-approved-568203.svg)](#)
[![by Aoxilus](https://img.shields.io/badge/by-Aoxilus-000000.svg)](https://github.com/aoxilus)

## 🆚 Why not Google Takeout? / ¿Por qué no Google Takeout?

**EN:** Google Takeout exports your mail as a giant `.mbox` file that's hard to use — you can't just open it and read your inbox. You need special software to import it, and there's no way to browse or search it like Gmail. **GhostTown** gives you a ready-to-read archive that looks and feels like Gmail, right in your browser.

**ES:** Google Takeout exporta tu correo como un enorme archivo `.mbox` difícil de usar — no puedes solo abrirlo y leer tu bandeja. Necesitas software especial para importarlo, y no hay forma de navegarlo ni buscarlo como en Gmail. **GhostTown** te da un archivo listo para leer que se ve y se siente como Gmail, directo en tu navegador.

## 📦 Get it / Consíguelo

**Option 1 — Release ZIP (easiest)**  
Open [Releases](../../releases), download `GhostTown-<version>.zip`, extract it.

**Option 2 — Clone / Fork**
```powershell
git clone https://github.com/aoxilus/GhostTown-.git
cd GhostTown-
```

Forks are welcome. Accepting pull requests is optional.

## 🚀 Windows

1. Install [Python 3.11+](https://www.python.org/downloads/) and select **Add Python to PATH**.
2. Double-click **`GhostTown.bat`**.
3. Follow the setup wizard. It opens Google and explains how to create the required Gmail App Password.
4. Browse your archive at **http://127.0.0.1:8765**

Your mail and credentials stay on your computer. They are never included in this repository or in GitHub releases.

Tus correos y credenciales permanecen en tu computadora. Nunca se incluyen en este repositorio ni en los releases de GitHub.

## ✨ Included / Incluye

- 📥 Gmail backup over IMAP / Respaldo de Gmail por IMAP
- 🖥️ Local Gmail-style archive / Archivo local estilo Gmail
- 📎 Attachments saved locally / Adjuntos guardados localmente
- 📊 Progress, folders, statistics, and backup log / Progreso, carpetas, estadísticas y log
- 🤖 Optional OpenAI-assisted cleanup with confirmation / Limpieza opcional con OpenAI y confirmación
- 🔒 Local credentials outside the app folder / Credenciales locales fuera de la app

## 📚 Docs

| Doc | |
|-----|--|
| [docs/VISION.md](docs/VISION.md) | Idea del proyecto |
| [docs/UI.md](docs/UI.md) | Stats, carpetas, paginación |
| [docs/SECURITY.md](docs/SECURITY.md) | Secretos y protecciones |

<p align="center"><a href="https://github.com/aoxilus"><b>Aoxilus</b></a> 🥑</p>
