@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==================================================
echo TRI-CAM SYNC ONE-CLICK SETUP  (Windows)
echo ==================================================
echo This installs Python, FFmpeg, Python packages,
echo and creates NOT UPLOADED\HEAD LEFT RIGHT on your SSD.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1"

echo.
pause
