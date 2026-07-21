<#
.SYNOPSIS
Builds and publishes a clean GhostTown release.

.DESCRIPTION
Run only from the private repository. The public repository receives one ZIP
asset containing the runtime files. Internal docs, agent rules, Git metadata,
credentials, mail, and generated archives are excluded by an explicit allowlist.

.EXAMPLE
.\scripts\Deploy-PublicRelease.ps1 -Version v0.2.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$')]
    [string]$Version,

    [string]$PublicRepo = "aoxilus/GhostTown-"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is required."
}

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Authenticate first with: gh auth login"
}

$dirty = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "This script must run inside the private Git repository."
}
if ($dirty) {
    throw "Commit or stash private repository changes before deploying."
}

$repoInfo = gh repo view $PublicRepo --json visibility --jq ".visibility"
if ($LASTEXITCODE -ne 0 -or $repoInfo -ne "PUBLIC") {
    throw "Public repository '$PublicRepo' does not exist or is not public."
}

gh release view $Version --repo $PublicRepo 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    throw "Release '$Version' already exists. Versions are immutable."
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) "ghosttown-release-$([guid]::NewGuid())"
$packageRoot = Join-Path $tempRoot "GhostTown-$Version"
$zipPath = Join-Path $tempRoot "GhostTown-$Version.zip"

try {
    New-Item -ItemType Directory -Path $packageRoot | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $packageRoot "scripts") | Out-Null

    # Explicit allowlist: never replace this with a recursive repository copy.
    Copy-Item "GhostTown.bat", "requirements.txt", ".env.example" -Destination $packageRoot
    Copy-Item "src", "templates" -Destination $packageRoot -Recurse
    Copy-Item "scripts/Start-GhostTown.ps1", "scripts/setup.ps1" `
        -Destination (Join-Path $packageRoot "scripts")
    Copy-Item "public/README.md" -Destination (Join-Path $packageRoot "README.md")

    $forbiddenNames = @(
        ".git", ".cursor", ".githooks", "AGENTS.md", "AI_SECURITY.md",
        ".env", "data", "ghosttown", "attachments"
    )
    $packagedPaths = Get-ChildItem $packageRoot -Recurse -Force |
        ForEach-Object { $_.FullName.Substring($packageRoot.Length + 1) }
    foreach ($name in $forbiddenNames) {
        if ($packagedPaths | Where-Object {
            $_ -eq $name -or $_ -like "$name\*" -or $_ -like "*\$name"
        }) {
            throw "Blocked forbidden release path: $name"
        }
    }

    Compress-Archive -Path $packageRoot -DestinationPath $zipPath -CompressionLevel Optimal

    $notes = @"
## 👻 GhostTown $Version 🥑

**EN:** Download the ZIP, extract it, and double-click ``GhostTown.bat``. The setup wizard guides you through Gmail access.

**ES:** Descarga el ZIP, descomprímelo y abre ``GhostTown.bat``. El asistente te guía para conectar Gmail.

### Privacy / Privacidad
- No credentials, email, attachments, or generated archives are included.
- No se incluyen credenciales, correos, adjuntos ni archivos generados.

**Aoxilus** 🥑
"@
    $notesPath = Join-Path $tempRoot "RELEASE_NOTES.md"
    Set-Content -Path $notesPath -Value $notes -Encoding UTF8

    gh release create $Version $zipPath `
        --repo $PublicRepo `
        --title "$Version - GhostTown 🥑" `
        --notes-file $notesPath `
        --latest
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub release creation failed."
    }

    Write-Host "Published: https://github.com/$PublicRepo/releases/tag/$Version"
}
finally {
    if (Test-Path $tempRoot) {
        Remove-Item $tempRoot -Recurse -Force
    }
}
