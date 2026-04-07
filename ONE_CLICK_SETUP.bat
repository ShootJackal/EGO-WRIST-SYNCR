@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==================================================
echo TRI-CAM SYNC ONE-CLICK SETUP
echo ==================================================
echo This installs Python, FFmpeg, Python packages,
echo and creates D:\NOT UPLOADED\HEAD LEFT RIGHT
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1"

echo.
pause
