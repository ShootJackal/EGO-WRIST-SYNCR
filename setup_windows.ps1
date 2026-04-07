param(
    [string]$ProjectRoot = "D:\NOT UPLOADED",
    [switch]$RunMatchAfterSetup = $false
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "=== $msg ===" -ForegroundColor Cyan
}

function Test-CommandExists($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Step "Checking winget"
if (-not (Test-CommandExists "winget")) {
    Write-Host "winget is not installed. Install App Installer / Windows Package Manager first, then re-run this script." -ForegroundColor Yellow
    exit 1
}

Write-Step "Installing Python"
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent

Write-Step "Installing FFmpeg"
winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements --silent

$pythonCmd = $null
if (Test-CommandExists "py") { $pythonCmd = "py" }
elseif (Test-CommandExists "python") { $pythonCmd = "python" }

if (-not $pythonCmd) {
    Write-Host "Python command not found after install. Close and reopen the terminal, then run setup again." -ForegroundColor Yellow
    exit 1
}

Write-Step "Installing Python packages"
& $pythonCmd -m pip install --upgrade pip
& $pythonCmd -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

Write-Step "Creating folder layout"
New-Item -ItemType Directory -Force -Path $ProjectRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "HEAD") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "LEFT") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "RIGHT") | Out-Null

Write-Step "Setup complete"
Write-Host "Put files in:" -ForegroundColor Green
Write-Host "  $ProjectRoot\HEAD"
Write-Host "  $ProjectRoot\LEFT"
Write-Host "  $ProjectRoot\RIGHT"

if ($RunMatchAfterSetup) {
    Write-Step "Running match"
    & $pythonCmd (Join-Path $PSScriptRoot "sync_pipeline.py") match --root $ProjectRoot
}
