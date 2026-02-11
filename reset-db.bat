@echo off
REM Script para reiniciar la base de datos (BORRA TODOS LOS DATOS)

echo ========================================
echo ADVERTENCIA: REINICIO DE BASE DE DATOS
echo ========================================
echo.
echo Este script eliminara TODOS los datos de la base de datos.
echo Esta accion NO se puede deshacer.
echo.
set /p confirm="Estas seguro? (escribe SI para continuar): "

if /i not "%confirm%"=="SI" (
    echo.
    echo Operacion cancelada.
    pause
    exit /b 0
)

echo.
echo Deteniendo servicios...
docker-compose down -v

if %errorlevel% neq 0 (
    echo [ERROR] No se pudo detener los servicios
    pause
    exit /b 1
)

echo.
echo Iniciando servicios con base de datos limpia...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] No se pudo iniciar los servicios
    pause
    exit /b 1
)

echo.
echo [OK] Base de datos reiniciada correctamente
echo.
echo Esperando a que PostgreSQL este listo...
timeout /t 5 /nobreak >nul

echo.
echo [OK] PostgreSQL esta listo para usar
echo.
pause
