<#
.SYNOPSIS
Publishes GhostTown to the private backup and the public open-source repo.

.DESCRIPTION
Source of truth = this private working tree.
Public repo gets an allowlisted open-source tree (code people can clone/fork)
plus a release ZIP. AI agent docs and deploy tools stay private.

.EXAMPLE
.\tools\Publish-GhostTown.ps1 -Version v0.2.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$')]
    [string]$Version,

    [string]$PrivateRemote = "private",
    [string]$PublicRepo = "aoxilus/GhostTown-",
    [switch]$SkipPublic,
    [switch]$SkipPrivatePush
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Assert-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Invoke-Gh {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GhArgs)
    & gh @GhArgs
    if ($LASTEXITCODE -ne 0) {
        throw "gh $($GhArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Ensure-Remote([string]$Name, [string]$Url) {
    $existing = git remote get-url $Name 2>$null
    if ($LASTEXITCODE -ne 0) {
        Invoke-Git remote add $Name $Url
    }
    elseif ($existing -ne $Url) {
        Invoke-Git remote set-url $Name $Url
    }
}

function New-PublicStaging([string]$Destination) {
    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Destination | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $Destination "scripts") | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $Destination "docs") | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $Destination ".githooks") | Out-Null

    # Explicit allowlist. Never replace with a recursive repository copy.
    Copy-Item "GhostTown.bat", "requirements.txt", ".env.example", ".gitignore" -Destination $Destination
    Copy-Item "src", "templates" -Destination $Destination -Recurse
    Copy-Item "scripts/Start-GhostTown.ps1", "scripts/setup.ps1" -Destination (Join-Path $Destination "scripts")
    Copy-Item ".githooks/pre-commit" -Destination (Join-Path $Destination ".githooks")
    Copy-Item "public/README.md" -Destination (Join-Path $Destination "README.md")
    Copy-Item "docs/VISION.md", "docs/UI.md" -Destination (Join-Path $Destination "docs")
    Copy-Item "public/docs/SECURITY.md" -Destination (Join-Path $Destination "docs/SECURITY.md")

    $forbidden = @(
        ".cursor", "AGENTS.md", "AI_SECURITY.md",
        ".env", "data", "ghosttown", "attachments",
        "internal", "tools", "bridge_progress.py",
        "Deploy-PublicRelease.ps1", "Publish-GhostTown.ps1"
    )
    $paths = Get-ChildItem $Destination -Recurse -Force |
        ForEach-Object { $_.FullName.Substring($Destination.Length + 1) }
    foreach ($name in $forbidden) {
        if ($paths | Where-Object {
                $_ -eq $name -or
                $_ -like "$name\*" -or
                $_ -like "*\$name" -or
                (Split-Path $_ -Leaf) -eq $name
            }) {
            throw "Blocked forbidden public path: $name"
        }
    }
}

Assert-Command git
Assert-Command gh
Invoke-Gh auth status | Out-Null

$dirty = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "Run this from the private GhostTown git working tree."
}
if ($dirty) {
    throw "Commit or stash local changes before publishing."
}

Ensure-Remote $PrivateRemote "https://github.com/aoxilus/GhostTown-Private.git"
Ensure-Remote "public" "https://github.com/$PublicRepo.git"

if (-not $SkipPrivatePush) {
    Write-Host "==> Pushing private source of truth ($PrivateRemote)"
    Invoke-Git push $PrivateRemote HEAD:main
}

if ($SkipPublic) {
    Write-Host "Skipped public publish."
    return
}

$visibility = gh repo view $PublicRepo --json visibility --jq ".visibility"
if ($LASTEXITCODE -ne 0 -or $visibility -ne "PUBLIC") {
    throw "Public repository '$PublicRepo' does not exist or is not public."
}

gh release view $Version --repo $PublicRepo 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    throw "Release '$Version' already exists. Versions are immutable."
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) "ghosttown-publish-$([guid]::NewGuid())"
$staging = Join-Path $tempRoot "tree"
$zipPath = Join-Path $tempRoot "GhostTown-$Version.zip"

try {
    Write-Host "==> Building open-source public tree"
    New-PublicStaging $staging

    Write-Host "==> Publishing public open-source main"
    Push-Location $staging
    try {
        Invoke-Git init -b main
        Invoke-Git config user.email "noreply@github.com"
        Invoke-Git config user.name "GhostTown Publisher"
        # Staging already contains only the allowlist.
        Invoke-Git add .
        Invoke-Git status --short
        Invoke-Git commit -m "release: $Version open source package"
        Invoke-Git remote add origin "https://github.com/$PublicRepo.git"
        # Orphan public history keeps AI/private docs out of public clones.
        Invoke-Git push --force origin main
    }
    finally {
        Pop-Location
    }

    Write-Host "==> Creating public release ZIP"
    Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $zipPath -CompressionLevel Optimal

    $notes = @"
## 👻 GhostTown $Version 🥑

**EN:** Clone the repo or download the ZIP. On Windows, extract and double-click ``GhostTown.bat``. The setup wizard guides you through Gmail access.

**ES:** Clona el repo o descarga el ZIP. En Windows, descomprime y abre ``GhostTown.bat``. El asistente te guía para conectar Gmail.

### Privacy / Privacidad
- No credentials, email, attachments, or generated archives are included.
- No se incluyen credenciales, correos, adjuntos ni archivos generados.

Forks are fine. Merging pull requests is optional.

**Aoxilus** 🥑
"@
    $notesPath = Join-Path $tempRoot "RELEASE_NOTES.md"
    Set-Content -Path $notesPath -Value $notes -Encoding UTF8

    Invoke-Gh release create $Version $zipPath `
        --repo $PublicRepo `
        --title "$Version - GhostTown 🥑" `
        --notes-file $notesPath `
        --latest

    Write-Host "Private:  https://github.com/aoxilus/GhostTown-Private"
    Write-Host "Public:   https://github.com/$PublicRepo"
    Write-Host "Release:  https://github.com/$PublicRepo/releases/tag/$Version"
}
finally {
    if (Test-Path $tempRoot) {
        Remove-Item $tempRoot -Recurse -Force
    }
}
