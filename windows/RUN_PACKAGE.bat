@echo off
setlocal
cd /d "%~dp0"

echo.
echo  TriCamSync - Package Matched Sets
echo  ===================================
echo.

set ROOT_ARG=
if not "%TRI_CAM_ROOT%"=="" (
    set ROOT_ARG=--root "%TRI_CAM_ROOT%"
)

"%~dp0TriCamSync.exe" package %ROOT_ARG%

echo.
pause
