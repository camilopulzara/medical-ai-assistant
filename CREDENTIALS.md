# 🔐 Credenciales de Desarrollo

## PostgreSQL (Docker)

```
Host: localhost
Port: 5432
Database: medical_ai_db
Username: medical_user
Password: medical_password_2026
```

**URL de Conexión:**
```
postgresql://medical_user:medical_password_2026@localhost:5432/medical_ai_db
```

## pgAdmin (Interfaz Web)

**URL:** http://localhost:5050

```
Email: admin@medical-ai.com
Password: admin
```

### Configurar servidor en pgAdmin:
1. Abrir http://localhost:5050
2. Login con las credenciales de arriba
3. Click derecho en "Servers" → "Register" → "Server"
4. Tab "General":
   - Name: `Medical AI DB`
5. Tab "Connection":
   - Host: `postgres` (nombre del contenedor)
   - Port: `5432`
   - Database: `medical_ai_db`
   - Username: `medical_user`
   - Password: `medical_password_2026`
   - ✓ Save password
6. Click "Save"

## Backend API

**Base URL:** http://localhost:8000

**Documentación Swagger:** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

## Frontend (Próximamente)

**URL:** http://localhost:3000

---

⚠️ **IMPORTANTE**: Estas credenciales son SOLO para desarrollo local.

**NUNCA** uses estas credenciales en producción.

Para producción:
1. Genera contraseñas seguras aleatorias
2. Usa variables de entorno
3. Usa servicios de gestión de secretos (AWS Secrets Manager, Azure Key Vault, etc.)
4. Nunca commitees credenciales al repositorio
