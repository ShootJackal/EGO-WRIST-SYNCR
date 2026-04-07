@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0sync_pipeline.py" package --root "D:\NOT UPLOADED"
) else (
    python "%~dp0sync_pipeline.py" package --root "D:\NOT UPLOADED"
)

echo.
pause
