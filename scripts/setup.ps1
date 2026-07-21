# setup.ps1 — venv + deps
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env; Write-Host "Edit .env then: python -m src.cli sync" }
Write-Host "OK. Activate: .\.venv\Scripts\Activate.ps1"
