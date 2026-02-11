# 🚀 Guía de Inicio Rápido - Medical AI Assistant Backend

## Pasos para ejecutar el backend

### 1️⃣ Activar entorno virtual

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
```

### 2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Iniciar PostgreSQL con Docker

```bash
# Desde la raíz del proyecto (no desde /backend)
cd ..
docker-compose up -d
```

Esto inicia PostgreSQL automáticamente. Verifica que esté corriendo:
```bash
docker-compose ps
```

### 4️⃣ Configurar variables de entorno

```bash
cd backend
copy .env.example .env
```

El archivo `.env` ya está configurado para Docker. Solo actualiza:
- `SECRET_KEY` (genera uno nuevo para producción)

### 5️⃣ Ejecutar el servidor

```bash
python main.py
```

### 6️⃣ Verificar que funciona

Abre tu navegador en:
- http://localhost:8000 (API root)
- http://localhost:8000/docs (Documentación Swagger)

## 🧪 Comandos de prueba

```bash
# Health check
curl http://localhost:8000/health

# Crear paciente
curl -X POST "http://localhost:8000/api/patients/" -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"name\":\"Test User\",\"phone\":\"555-0000\"}"

# Listar pacientes
curl http://localhost:8000/api/patients/
```

## ⚠️ Solución de problemas

**Error: No module named 'fastapi'**
- Solución: Asegúrate de tener el venv activado y ejecuta `pip install -r requirements.txt`

**Error: Could not connect to database**
- Solución: Verifica que PostgreSQL esté corriendo y que la URL en `.env` sea correcta

**Error: Port 8000 already in use**
- Solución: Cambia el puerto en `.env` o mata el proceso que usa el puerto 8000
