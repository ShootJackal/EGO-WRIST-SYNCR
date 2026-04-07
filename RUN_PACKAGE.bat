@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0sync_pipeline.py" package
) else (
    python "%~dp0sync_pipeline.py" package
)

echo.
pause
