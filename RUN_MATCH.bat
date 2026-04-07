@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0match_3cams.py"
) else (
    python "%~dp0match_3cams.py"
)

echo.
pause
