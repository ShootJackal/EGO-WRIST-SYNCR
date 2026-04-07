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

function Get-SystemDriveLetter {
    $sd = $env:SystemDrive
    if ($sd) { return $sd.Substring(0,1).ToUpper() }
    return "C"
}

function Get-ExternalDrives {
    $sysLetter = Get-SystemDriveLetter
    return Get-PSDrive -PSProvider FileSystem |
        Where-Object { $_.Name.ToUpper() -ne $sysLetter } |
        Sort-Object Name
}

function Prompt-ForRoot {
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Yellow
    Write-Host "  No external drive with 'NOT UPLOADED\HEAD\LEFT\RIGHT'" -ForegroundColor Yellow
    Write-Host "  was found automatically." -ForegroundColor Yellow
    Write-Host ("=" * 60) -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please enter a drive letter or full path to the"
    Write-Host "'NOT UPLOADED' folder."
    Write-Host ""
    Write-Host "  Examples:"
    Write-Host "    E"
    Write-Host "    E:\NOT UPLOADED"
    Write-Host "    F:\MyProject\NOT UPLOADED"
    Write-Host ""

    while ($true) {
        $response = Read-Host "Drive letter or path"
        if (-not $response -or $response.Trim().Length -eq 0) { continue }
        $response = $response.Trim()

        if ($response.Length -eq 1 -and $response -match '^[A-Za-z]$') {
            $candidate = Join-Path ($response.ToUpper() + ":\") "NOT UPLOADED"
        } elseif ($response.Length -eq 2 -and $response -match '^[A-Za-z]:$') {
            $candidate = Join-Path ($response.Substring(0,1).ToUpper() + ":\") "NOT UPLOADED"
        } else {
            $candidate = $response
        }

        if (Test-Path $candidate) {
            return $candidate
        }

        $drivePart = Split-Path -Qualifier $candidate -ErrorAction SilentlyContinue
        if ($drivePart -and (Test-Path ($drivePart + "\"))) {
            Write-Host "  Path '$candidate' does not exist yet."
            $confirm = Read-Host "  Create and use it anyway? (y/n)"
            if ($confirm -match '^[Yy]') { return $candidate }
        } else {
            Write-Host "  Drive or path '$candidate' does not exist. Please try again." -ForegroundColor Red
        }
    }
}

function Resolve-ProjectRoot([string]$ProvidedRoot) {
    if ($ProvidedRoot -and $ProvidedRoot.Trim().Length -gt 0) {
        return $ProvidedRoot
    }

    if ($env:TRI_CAM_ROOT -and $env:TRI_CAM_ROOT.Trim().Length -gt 0) {
        return $env:TRI_CAM_ROOT
    }

    $externalDrives = Get-ExternalDrives
    foreach ($d in $externalDrives) {
        $candidate = Join-Path ($d.Name + ":\") "NOT UPLOADED"
        $hasLayout = (Test-Path (Join-Path $candidate "HEAD")) -and `
                     (Test-Path (Join-Path $candidate "LEFT")) -and `
                     (Test-Path (Join-Path $candidate "RIGHT"))
        if ($hasLayout) {
            return $candidate
        }
    }

    foreach ($d in $externalDrives) {
        $candidate = Join-Path ($d.Name + ":\") "NOT UPLOADED"
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return Prompt-ForRoot
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
Write-Host "     Example: setx TRI_CAM_ROOT ""E:\NOT UPLOADED""" -ForegroundColor DarkGray

if ($RunMatchAfterSetup) {
    Write-Step "Running match"
    & $pythonCmd (Join-Path $PSScriptRoot "sync_pipeline.py") match --root $ResolvedRoot
}
