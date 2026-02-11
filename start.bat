@echo off
REM Script de inicio rápido para Medical AI Assistant
REM Windows Batch Script

echo ========================================
echo Medical AI Assistant - Inicio Rapido
echo ========================================
echo.

REM Verificar si Docker está corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo.
    echo Por favor, inicia Docker Desktop y vuelve a ejecutar este script.
    pause
    exit /b 1
)

echo [OK] Docker esta corriendo
echo.

REM Iniciar Docker Compose
echo Iniciando PostgreSQL con Docker...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] No se pudo iniciar Docker Compose
    pause
    exit /b 1
)

echo.
echo [OK] PostgreSQL iniciado correctamente
echo.

REM Esperar a que PostgreSQL esté listo
echo Esperando a que PostgreSQL este listo...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Servicios disponibles:
echo ========================================
echo - PostgreSQL: localhost:5432
echo - pgAdmin: http://localhost:5050
echo   Usuario: admin@medical-ai.com
echo   Password: admin
echo.
echo ========================================
echo Siguiente paso:
echo ========================================
echo 1. Abre otra terminal
echo 2. cd backend
echo 3. python -m venv venv
echo 4. .\venv\Scripts\activate
echo 5. pip install -r requirements.txt
echo 6. copy .env.example .env
echo 7. python main.py
echo.

pause
