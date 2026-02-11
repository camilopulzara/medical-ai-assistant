# Entorno Virtual Python - Backend

## Configuración Completada ✓

Se ha creado exitosamente un entorno virtual con **Python 3.10.10** y todas las dependencias necesarias.

### Ubicación del Python
- **Ruta**: `C:\Users\pulzara\AppData\Local\Programs\Python\Python310`
- **Versión**: Python 3.10.10

### Entorno Virtual
- **Carpeta**: `backend/venv/`
- **Activación**: Ejecutar `activate.bat` o `venv\Scripts\Activate.ps1`

## Dependencias Instaladas

### Framework Web
- **FastAPI** 0.109.0 - Framework web moderno y rápido
- **Uvicorn** 0.27.0 - Servidor ASGI
- **Starlette** 0.35.1 - Framework web ligero
- **Pydantic** 2.12.5 - Validación de datos
- **WebSockets** 12.0 - Soporte para WebSockets

### Base de Datos
- **SQLAlchemy** 2.0.25 - ORM para base de datos
- **psycopg2-binary** 2.9.9 - Driver PostgreSQL
- **Alembic** 1.13.1 - Migraciones de base de datos

### Inteligencia Artificial y LangChain
- **LangChain** 1.2.9 - Framework para aplicaciones con LLMs
- **LangChain-Core** 1.2.9 - Núcleo de LangChain
- **LangChain-OpenAI** 1.1.8 - Integración con OpenAI
- **LangChain-Community** 0.4.1 - Integraciones comunitarias
- **LangGraph** 1.0.8 - Grafos para agentes de IA
- **LangSmith** 0.7.1 - Observabilidad para LangChain

### Machine Learning
- **PyTorch** 2.2.0 (CPU version) - Framework de deep learning
- **Transformers** 4.37.0 - Modelos de lenguaje pre-entrenados
- **Tokenizers** 0.15.2 - Tokenización rápida
- **SafeTensors** 0.7.0 - Almacenamiento seguro de tensores
- **NumPy** 2.2.6 - Computación numérica

### OpenAI
- **OpenAI** 2.18.0 - SDK oficial de OpenAI
- **Tiktoken** 0.12.0 - Tokenizador de OpenAI

### Seguridad y Autenticación
- **python-jose** 3.3.0 - JWT tokens
- **passlib** 1.7.4 - Hashing de contraseñas
- **bcrypt** 5.0.0 - Algoritmo de hashing
- **cryptography** 46.0.4 - Primitivas criptográficas
- **email-validator** 2.1.0 - Validación de emails

### Utilidades
- **python-dotenv** 1.0.0 - Variables de entorno
- **aiohttp** 3.13.3 - Cliente HTTP asíncrono
- **httpx** 0.28.1 - Cliente HTTP moderno
- **requests** 2.32.5 - Cliente HTTP sincrónico
- **tqdm** 4.67.3 - Barras de progreso

## Uso del Entorno Virtual

### Windows (PowerShell)
```powershell
# Activar
.\venv\Scripts\Activate.ps1

# Desactivar
deactivate
```

### Windows (CMD)
```cmd
# Activar
venv\Scripts\activate.bat
# o simplemente
activate.bat

# Desactivar
deactivate
```

## Verificar Instalación

```powershell
# Ver versión de Python
python --version

# Listar paquetes instalados
pip list

# Ver información específica de un paquete
pip show fastapi
```

## Ejecutar el Backend

```powershell
# 1. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 2. Ejecutar el servidor
uvicorn main:app --reload

# o con configuración específica
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Agregar Nuevas Dependencias

```powershell
# Instalar un paquete
pip install nombre-paquete

# Actualizar requirements.txt
pip freeze > requirements-updated.txt
```

## Notas Importantes

1. **Siempre activa el entorno virtual antes de trabajar** en el proyecto
2. Las dependencias de IA/ML son pesadas (~200MB+ para PyTorch)
3. Para GPU, necesitarás reinstalar PyTorch con soporte CUDA
4. El entorno usa Python 3.10 específicamente para compatibilidad

## Solución de Problemas

### Error al activar en PowerShell
```powershell
# Ejecutar como administrador
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Reinstalar dependencias
```powershell
pip install -r requirements.txt --force-reinstall
```

### Limpiar cache de pip
```powershell
pip cache purge
```

---

**Fecha de creación**: 9 de febrero de 2026  
**Python versión**: 3.10.10  
**Entorno**: Windows
