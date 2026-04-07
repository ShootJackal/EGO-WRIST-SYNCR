@echo off
setlocal
cd /d "%~dp0"

echo.
echo  TriCamSync - FFmpeg Installer
echo  ==============================
echo  This installs FFmpeg which is required for audio processing.
echo  You only need to run this once.
echo.

where ffmpeg >nul 2>nul
if %errorlevel%==0 (
    echo FFmpeg is already installed. You're good to go!
    echo.
    pause
    exit /b 0
)

echo Installing FFmpeg via winget...
winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements --silent

echo.
echo Done! You may need to restart your computer for FFmpeg to be available.
echo.
pause
