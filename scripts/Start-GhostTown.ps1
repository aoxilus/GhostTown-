<#
  Start-GhostTown.ps1
  GUI launcher: pide credenciales, verifica el login IMAP y abre GhostTown.
  Doble clic recomendado desde GhostTown.bat (evita problemas de ExecutionPolicy).
#>

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$root = Split-Path $PSScriptRoot -Parent
$py = Join-Path $root ".venv\Scripts\python.exe"
$envFile = Join-Path $root ".env"

function Show-Info($msg, $title = "GhostTown") {
    [System.Windows.Forms.MessageBox]::Show($msg, $title,
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
}

# ---------- 1. Asegurar entorno Python (venv + dependencias) ----------
Push-Location $root
try {
    if (-not (Test-Path $py)) {
        Write-Host "Instalando entorno por primera vez (puede tardar 1-2 min)..." -ForegroundColor Yellow
        python -m venv .venv
        & $py -m pip install --quiet --upgrade pip
        & $py -m pip install --quiet -r requirements.txt
        Write-Host "Entorno listo." -ForegroundColor Green
    }
}
catch {
    Show-Info "No se pudo preparar Python. Instala Python 3.11+ desde python.org y vuelve a intentar.`n`n$($_.Exception.Message)" "Error"
    Pop-Location
    return
}
Pop-Location

# ---------- 2. Cargar valores previos del .env si existen ----------
$prev = @{ IMAP_USER = ""; IMAP_PASSWORD = ""; OPENAI_API_KEY = "" }
if (Test-Path $envFile) {
    foreach ($line in Get-Content $envFile) {
        if ($line -match "^\s*([A-Z_]+)\s*=\s*(.*)$") {
            $k = $matches[1]; $v = $matches[2]
            if ($prev.ContainsKey($k) -and $v -notmatch "^(xxxx|tu@|sk-\.\.\.)") { $prev[$k] = $v }
        }
    }
}

# ---------- 3. Construir la ventana ----------
$form = New-Object System.Windows.Forms.Form
$form.Text = "GmailGhostTown"
$form.Size = New-Object System.Drawing.Size(480, 430)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.BackColor = [System.Drawing.Color]::FromArgb(42, 36, 28)
$form.ForeColor = [System.Drawing.Color]::FromArgb(232, 220, 200)

function New-Label($text, $y) {
    $l = New-Object System.Windows.Forms.Label
    $l.Text = $text
    $l.Location = New-Object System.Drawing.Point(20, $y)
    $l.Size = New-Object System.Drawing.Size(430, 20)
    $l.ForeColor = [System.Drawing.Color]::FromArgb(196, 180, 154)
    $form.Controls.Add($l)
    return $l
}

function New-Box($y, $mask) {
    $t = New-Object System.Windows.Forms.TextBox
    $t.Location = New-Object System.Drawing.Point(20, $y)
    $t.Size = New-Object System.Drawing.Size(430, 24)
    if ($mask) { $t.UseSystemPasswordChar = $true }
    $form.Controls.Add($t)
    return $t
}

$title = New-Object System.Windows.Forms.Label
$title.Text = "GmailGhostTown"
$title.Location = New-Object System.Drawing.Point(20, 12)
$title.Size = New-Object System.Drawing.Size(430, 28)
$title.Font = New-Object System.Drawing.Font("Consolas", 15, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($title)

New-Label "Correo Gmail:" 55 | Out-Null
$tbUser = New-Box 76 $false
$tbUser.Text = $prev.IMAP_USER

New-Label "App Password (16 letras de Google, NO tu clave normal):" 108 | Out-Null
$tbPass = New-Box 129 $true
$tbPass.Text = $prev.IMAP_PASSWORD

New-Label "OpenAI API Key (opcional, solo para limpiar con IA):" 161 | Out-Null
$tbKey = New-Box 182 $true
$tbKey.Text = $prev.OPENAI_API_KEY

$help = New-Object System.Windows.Forms.LinkLabel
$help.Text = "Como crear el App Password (pasos)"
$help.Location = New-Object System.Drawing.Point(20, 214)
$help.Size = New-Object System.Drawing.Size(430, 20)
$help.LinkColor = [System.Drawing.Color]::FromArgb(196, 180, 154)
$help.Add_LinkClicked({
    $steps = @"
COMO CREAR EL APP PASSWORD (una sola vez)

1. Entra a tu Cuenta de Google (la personal, no la escolar).
2. Activa la Verificacion en 2 pasos:
   myaccount.google.com/security  ->  Verificacion en 2 pasos  ->  Activar.
3. Activa IMAP en Gmail:
   Gmail  ->  Configuracion  ->  Reenvio y correo POP/IMAP  ->  Habilitar IMAP.
4. Crea el App Password:
   myaccount.google.com/apppasswords
   - Nombre de la app: escribe  GhostTown
   - Clic en Crear.
5. Google te da 16 letras (ejemplo: abcd efgh ijkl mnop).
   Copialas aqui en 'App Password' (los espacios no importan).

Se abrira la pagina de App Passwords ahora.
"@
    Show-Info $steps "Guia App Password"
    Start-Process "https://myaccount.google.com/apppasswords"
})
$form.Controls.Add($help)

$status = New-Object System.Windows.Forms.Label
$status.Location = New-Object System.Drawing.Point(20, 244)
$status.Size = New-Object System.Drawing.Size(430, 40)
$status.ForeColor = [System.Drawing.Color]::FromArgb(220, 180, 120)
$form.Controls.Add($status)

$btn = New-Object System.Windows.Forms.Button
$btn.Text = "Verificar y abrir GhostTown"
$btn.Location = New-Object System.Drawing.Point(20, 300)
$btn.Size = New-Object System.Drawing.Size(430, 44)
$btn.BackColor = [System.Drawing.Color]::FromArgb(58, 42, 26)
$btn.ForeColor = [System.Drawing.Color]::FromArgb(196, 180, 154)
$btn.FlatStyle = "Flat"
$form.Controls.Add($btn)

$script:verified = $false

$btn.Add_Click({
    $user = $tbUser.Text.Trim()
    $pass = ($tbPass.Text -replace "\s", "")
    $key = $tbKey.Text.Trim()

    if (-not $user -or -not $pass) {
        $status.Text = "Escribe tu Gmail y el App Password."
        return
    }

    # Escribir .env
    $lines = @(
        "IMAP_HOST=imap.gmail.com",
        "IMAP_USER=$user",
        "IMAP_PASSWORD=$pass",
        "OPENAI_API_KEY=$key",
        "OPENAI_MODEL=gpt-4.1-mini",
        "PORT=8765"
    )
    Set-Content -Path $envFile -Value $lines -Encoding UTF8

    $status.Text = "Verificando login con Google..."
    $btn.Enabled = $false
    $form.Refresh()

    Push-Location $root
    $out = & $py -m src.cli verify 2>&1
    $code = $LASTEXITCODE
    Pop-Location

    if ($code -eq 0) {
        $status.ForeColor = [System.Drawing.Color]::FromArgb(140, 200, 140)
        $status.Text = "Login correcto. Abriendo GhostTown..."
        $form.Refresh()
        $script:verified = $true
        $form.Close()
    }
    else {
        $reason = "$out"
        try { $reason = ($out | Select-Object -Last 1 | ConvertFrom-Json).error } catch {}
        $status.ForeColor = [System.Drawing.Color]::FromArgb(220, 120, 120)
        $status.Text = "No se pudo entrar: $reason"
        $btn.Enabled = $true
    }
})

[void]$form.ShowDialog()

# ---------- 4. Si verifico, bajar correo y abrir GhostTown ----------
if ($script:verified) {
    Push-Location $root
    Write-Host "`nBajando correo (primer sync limitado a 200 para ir rapido)..." -ForegroundColor Cyan
    & $py -m src.cli sync --limit 200
    Write-Host "`nAbriendo GhostTown en http://127.0.0.1:8765 ..." -ForegroundColor Green
    Start-Process "http://127.0.0.1:8765"
    & $py -m src.cli serve --no-browser
    Pop-Location
}
