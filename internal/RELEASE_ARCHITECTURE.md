# Release architecture (private only)

## Model: open source public + private internals

- `aoxilus/GhostTown-Private` — full source of truth: code, history, AI agent rules, deploy tools.
- `aoxilus/GhostTown-` — public open source mirror: runnable code people can clone, fork, and download as releases.

Forks are welcome to exist. Accepting pull requests is optional and separate.

Neither repo may contain credentials, real email, attachments, `data/`, or generated `ghosttown/` archives.

## Folder roles (this working tree)

| Path | Private | Public |
|------|---------|--------|
| `src/`, `templates/` | yes | yes |
| `scripts/Start-GhostTown.ps1`, `scripts/setup.ps1` | yes | yes |
| `GhostTown.bat`, `requirements.txt`, `.env.example`, `.gitignore` | yes | yes |
| `.githooks/` | yes | yes |
| `public/README.md` → public `README.md` | yes | yes |
| `docs/VISION.md`, `docs/UI.md`, `docs/SECURITY.md` (sanitized copy) | yes | yes |
| `AGENTS.md`, `.cursor/`, `docs/AI_SECURITY.md` | yes | **no** |
| `tools/`, `internal/`, `scripts/bridge_progress.py` | yes | **no** |
| `data/`, `ghosttown/`, `.env` | local only | **never** |

## One command

```powershell
.\tools\Publish-GhostTown.ps1 -Version v0.2.0
```

What it does:

1. Pushes the private repo (backup / source of truth).
2. Builds an allowlisted open-source tree.
3. Force-publishes that tree to the public `main` (orphan history, no AI docs).
4. Creates a public GitHub Release ZIP from the same tree.

Versions are immutable. Use a new semantic version every time.
