# 🧪 Guía de Pruebas - Medical AI Assistant

## ✅ Estado Actual

### Docker y PostgreSQL: FUNCIONANDO ✅

Los contenedores están corriendo correctamente:
- **PostgreSQL**: `localhost:5432` (healthy)
- **pgAdmin**: `http://localhost:5050` (activo)

### Base de Datos: LISTA ✅

Tablas creadas:
- ✅ patients (2 registros de prueba)
- ✅ appointments
- ✅ chat_sessions
- ✅ chat_messages
- ✅ documents

---

## 🧪 Pruebas Disponibles

### 1. **pgAdmin (Interfaz Gráfica)** ⭐ Recomendado

Abre tu navegador en: **http://localhost:5050**

**Login:**
- Email: `admin@medical-ai.com`
- Password: `admin`

**Conectar al servidor PostgreSQL:**
1. Click derecho en "Servers" → "Register" → "Server"
2. **General Tab:**
   - Name: `Medical AI DB`
3. **Connection Tab:**
   - Host: `postgres` (nombre del contenedor)
   - Port: `5432`
   - Database: `medical_ai_db`
   - Username: `medical_user`
   - Password: `medical_password_2026`
   - ✓ Save password
4. Click "Save"

**Ver datos:**
- Servers → Medical AI DB → Databases → medical_ai_db → Schemas → public → Tables
- Click derecho en "patients" → "View/Edit Data" → "All Rows"

---

### 2. **PostgreSQL desde Terminal**

```powershell
# Ver todas las tablas
docker exec medical-ai-postgres psql -U medical_user -d medical_ai_db -c "\dt"

# Ver pacientes
docker exec medical-ai-postgres psql -U medical_user -d medical_ai_db -c "SELECT * FROM patients;"

# Ver citas
docker exec medical-ai-postgres psql -U medical_user -d medical_ai_db -c "SELECT * FROM appointments;"

# Insertar un nuevo paciente
docker exec medical-ai-postgres psql -U medical_user -d medical_ai_db -c "INSERT INTO patients (email, name, phone) VALUES ('test@example.com', 'Test User', '555-9999');"

# Crear una cita
docker exec medical-ai-postgres psql -U medical_user -d medical_ai_db -c "INSERT INTO appointments (patient_id, appointment_date, reason, status) VALUES (1, '2026-02-10 10:00:00', 'Consulta general', 'pending');"
```

---

### 3. **Probar Backend API** (Cuando el venv esté arreglado)

Una vez que el servidor FastAPI esté corriendo, probar con **PowerShell**:

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Listar pacientes
Invoke-RestMethod -Uri "http://localhost:8000/api/patients/"

# Crear paciente
$body = @{
    email = "nuevo@example.com"
    name = "Nuevo Paciente"
    phone = "555-0000"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/patients/" -Method POST -Body $body -ContentType "application/json"

# Crear cita
$body = @{
    patient_email = "juan.perez@example.com"
    appointment_date = "2026-02-15T14:30:00"
    reason = "Control anual"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/appointments/" -Method POST -Body $body -ContentType "application/json"
```

O desde el navegador:
- **Swagger UI**: http://localhost:8000/docs (interfaz interactiva)
- **ReDoc**: http://localhost:8000/redoc

---

### 4. **Verificar Logs de Docker**

```powershell
# Ver logs de PostgreSQL
docker logs medical-ai-postgres --tail 50

# Ver logs de pgAdmin
docker logs medical-ai-pgadmin --tail 50

# Seguir logs en tiempo real
docker logs -f medical-ai-postgres
```

---

### 5. **Gestión de Docker**

```powershell
# Ver estado de contenedores
docker-compose ps

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose stop

# Iniciar servicios
docker-compose start

# Ver logs de todos los servicios
docker-compose logs -f
```

---

## 📊 Datos de Prueba Disponibles

### Pacientes:
1. **Juan Pérez**
   - Email: `juan.perez@example.com`
   - Teléfono: `555-1234`

2. **María García**
   - Email: `maria.garcia@example.com`
   - Teléfono: `555-5678`

---

## 🔧 Resolver el problema del Backend

Para que el servidor FastAPI funcione, necesitas arreglar el entorno virtual:

### Opción 1: Reiniciar Windows y recrear el venv
```powershell
# Después de reiniciar:
cd E:\repositorios\R\medical-ai-assistant\backend
Remove-Item -Recurse -Force .venv
C:\Users\pulzara\AppData\Local\Programs\Python\Python310\python.exe -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-basic.txt
python main.py
```

### Opción 2: Usar venv temporal
```powershell
cd backend
C:\Users\pulzara\AppData\Local\Programs\Python\Python310\python.exe -m venv venv_temp
.\venv_temp\Scripts\activate
pip install -r requirements-basic.txt
python main.py
```

---

## 🎯 Resumen

| Componente | Estado | URL/Comando |
|------------|--------|-------------|
| Docker | ✅ Funcionando | `docker ps` |
| PostgreSQL | ✅ Funcionando | `localhost:5432` |
| pgAdmin | ✅ Funcionando | http://localhost:5050 |
| Base de Datos | ✅ Creada | 5 tablas + datos |
| Backend API | ⏳ Pendiente | Requiere arreglar venv |

**¡PostgreSQL y Docker están 100% funcionales!** 🎉

Solo falta arreglar el entorno virtual de Python para que el servidor FastAPI arranque.
