param(
    [string]$ProjectRoot = "",
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

function Resolve-ProjectRoot([string]$ProvidedRoot) {
    if ($ProvidedRoot -and $ProvidedRoot.Trim().Length -gt 0) {
        return $ProvidedRoot
    }

    # Prefer any existing <Drive>:\NOT UPLOADED (works for external SSDs too)
    $drives = Get-PSDrive -PSProvider FileSystem | Sort-Object Name
    foreach ($d in $drives) {
        $candidate = Join-Path ($d.Name + ":\") "NOT UPLOADED"
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    # Otherwise create on first non-system drive, fallback to D:, then C:
    $nonSystem = $drives | Where-Object { $_.Name -ne "C" } | Select-Object -First 1
    if ($nonSystem) {
        return (Join-Path ($nonSystem.Name + ":\") "NOT UPLOADED")
    }

    if (Test-Path "D:\") {
        return "D:\NOT UPLOADED"
    }

    return "C:\NOT UPLOADED"
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

$ResolvedRoot = Resolve-ProjectRoot $ProjectRoot

Write-Step "Creating folder layout"
New-Item -ItemType Directory -Force -Path $ResolvedRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ResolvedRoot "HEAD") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ResolvedRoot "LEFT") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ResolvedRoot "RIGHT") | Out-Null

Write-Step "Setup complete"
Write-Host "Using project root:" -ForegroundColor Green
Write-Host "  $ResolvedRoot"
Write-Host "Put files in:" -ForegroundColor Green
Write-Host "  $ResolvedRoot\HEAD"
Write-Host "  $ResolvedRoot\LEFT"
Write-Host "  $ResolvedRoot\RIGHT"
Write-Host ""
Write-Host "Tip: set TRI_CAM_ROOT to pin a specific SSD path." -ForegroundColor DarkGray
Write-Host "     Example: setx TRI_CAM_ROOT \"E:\NOT UPLOADED\"" -ForegroundColor DarkGray

if ($RunMatchAfterSetup) {
    Write-Step "Running match"
    & $pythonCmd (Join-Path $PSScriptRoot "sync_pipeline.py") match --root $ResolvedRoot
}
