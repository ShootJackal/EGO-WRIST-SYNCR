@echo off
setlocal
cd /d "%~dp0"

set ROOT_ARG=
if not "%TRI_CAM_ROOT%"=="" (
    set ROOT_ARG=--root "%TRI_CAM_ROOT%"
)

where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0sync_pipeline.py" package %ROOT_ARG%
) else (
    python "%~dp0sync_pipeline.py" package %ROOT_ARG%
)

echo.
pause
