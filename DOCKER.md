# Docker Setup - Medical AI Assistant

## 🐳 Configuración con Docker

Este proyecto usa Docker para PostgreSQL, facilitando el desarrollo sin necesidad de instalar PostgreSQL localmente.

## Prerequisitos

- **Docker Desktop** instalado y corriendo
- **Docker Compose** (viene con Docker Desktop)

## 🚀 Inicio Rápido

### 1. Iniciar PostgreSQL con Docker

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

Esto iniciará:
- **PostgreSQL** en `localhost:5432`
- **pgAdmin** (interfaz web) en `http://localhost:5050`

### 2. Verificar que los contenedores están corriendo

```bash
docker-compose ps
```

Deberías ver:
```
NAME                    STATUS
medical-ai-postgres     Up
medical-ai-pgadmin      Up
```

### 3. Configurar el backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
copy .env.example .env
```

El archivo `.env` ya está configurado para Docker, no necesitas cambiar nada.

### 4. Iniciar el backend

```bash
python main.py
```

## 🔧 Comandos Útiles

### Detener los contenedores
```bash
docker-compose stop
```

### Iniciar contenedores detenidos
```bash
docker-compose start
```

### Ver logs de PostgreSQL
```bash
docker-compose logs -f postgres
```

### Reiniciar PostgreSQL
```bash
docker-compose restart postgres
```

### Detener y eliminar contenedores (mantiene los datos)
```bash
docker-compose down
```

### Eliminar TODO (incluye datos de la base de datos)
⚠️ **CUIDADO**: Esto borrará todos los datos
```bash
docker-compose down -v
```

## 🗄️ Acceder a PostgreSQL

### Opción 1: pgAdmin (Interfaz Web)
1. Abre http://localhost:5050
2. Login:
   - Email: `admin@medical-ai.com`
   - Password: `admin`
3. Agregar servidor:
   - Host: `postgres` (nombre del servicio en Docker)
   - Port: `5432`
   - Database: `medical_ai_db`
   - Username: `medical_user`
   - Password: `medical_password_2026`

### Opción 2: Línea de comandos (psql)
```bash
docker exec -it medical-ai-postgres psql -U medical_user -d medical_ai_db
```

### Opción 3: Cliente externo (DBeaver, DataGrip, etc.)
```
Host: localhost
Port: 5432
Database: medical_ai_db
Username: medical_user
Password: medical_password_2026
```

## 📊 Credenciales

### PostgreSQL
- **Host**: localhost
- **Puerto**: 5432
- **Base de datos**: medical_ai_db
- **Usuario**: medical_user
- **Contraseña**: medical_password_2026

### pgAdmin
- **URL**: http://localhost:5050
- **Email**: admin@medical-ai.com
- **Contraseña**: admin

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Las credenciales en `docker-compose.yml` son solo para desarrollo local.

Para producción:
1. Cambia todas las contraseñas
2. Usa variables de entorno
3. No commitees credenciales al repositorio

## 🐛 Solución de Problemas

### Error: "port is already allocated"
```bash
# Ver qué está usando el puerto 5432
netstat -ano | findstr :5432

# Cambiar el puerto en docker-compose.yml
ports:
  - "5433:5432"  # Usar 5433 en lugar de 5432
```

### Error: "Cannot connect to the Docker daemon"
- Asegúrate de que Docker Desktop está corriendo
- Reinicia Docker Desktop

### La base de datos no persiste los datos
- Verifica que los volúmenes estén creados: `docker volume ls`
- No uses `docker-compose down -v` si quieres mantener los datos

### Resetear la base de datos
```bash
# Eliminar todo y empezar de cero
docker-compose down -v
docker-compose up -d
```

## 📦 Estructura de Volúmenes

Los datos se guardan en volúmenes de Docker:
- `postgres_data`: Datos de PostgreSQL
- `pgadmin_data`: Configuración de pgAdmin

Ver volúmenes:
```bash
docker volume ls
```

Inspeccionar volumen:
```bash
docker volume inspect medical-ai-assistant_postgres_data
```

## 🚢 Próximos Pasos

Cuando el backend completo esté listo, puedes:
1. Agregar el servicio de FastAPI a `docker-compose.yml`
2. Agregar el frontend de Next.js
3. Configurar networking entre servicios
4. Agregar Redis para caché (opcional)

Ejemplo futuro:
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```
