@echo off
REM Script para activar el entorno virtual de Python 3.10
REM Ubicación: backend\activate.bat

echo Activando entorno virtual de Python 3.10...
call venv\Scripts\activate.bat

echo.
echo Entorno virtual activado correctamente.
echo Python version:
python --version
echo.
echo Para desactivar el entorno, ejecuta: deactivate
