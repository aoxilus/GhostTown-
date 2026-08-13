$ErrorActionPreference = "Stop"

# Ruta de PyInstaller en el entorno virtual
$pyinstaller = ".\.venv\Scripts\pyinstaller.exe"

# Ejecutamos PyInstaller
# --onefile para un solo .exe
# --name "GhostTown"
# --add-data "templates;templates" para incluir el frontend (Jinja)
# src/cli.py es el entrypoint

Write-Host "Building GhostTown.exe..." -ForegroundColor Cyan

& $pyinstaller --clean --onefile --name "GhostTown" --add-data "templates;templates" "src/cli.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! Executable is located in the dist/ folder." -ForegroundColor Green
} else {
    Write-Host "Build failed." -ForegroundColor Red
}
