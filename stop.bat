@echo off
REM Script para detener los servicios de Docker

echo Deteniendo servicios de Docker...
docker-compose stop

if %errorlevel% equ 0 (
    echo.
    echo [OK] Servicios detenidos correctamente
) else (
    echo.
    echo [ERROR] Hubo un problema al detener los servicios
)

echo.
pause
