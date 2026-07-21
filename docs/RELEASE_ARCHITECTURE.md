# Release architecture (private)

## Repositories

- `aoxilus/GhostTown-Private`: source, history, internal documentation, security rules, and deployment tooling.
- `aoxilus/GhostTown-`: public landing page and downloadable release ZIPs only.

Neither repository may contain credentials, real email, attachments, `data/`, or generated `ghosttown/` archives.

## Public package

`scripts/Deploy-PublicRelease.ps1` builds from an explicit allowlist:

- `GhostTown.bat`
- `requirements.txt`
- `.env.example` with placeholders
- `src/`
- `templates/`
- user-facing launcher/setup scripts
- `public/README.md`, renamed to `README.md`

It excludes internal documentation, agent configuration, Git hooks, Git metadata, local data, and credentials.

## Publish

From a clean private working tree:

```powershell
.\scripts\Deploy-PublicRelease.ps1 -Version v0.2.0
```

Versions are immutable. Use a new semantic version for every deployment.
