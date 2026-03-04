# 🏥 Medical AI Assistant

Asistente médico inteligente que conversa con pacientes, gestiona citas y documentos automáticamente usando IA conversacional.

## 🎯 Características

- 💬 **Chat inteligente en tiempo real** con interfaz completa
- 🤖 **IA conversacional avanzada** con LangGraph + Groq API (llama-3.3-70b-versatile)
- 🧠 **Memoria conversacional** con historial de 8 mensajes
- 🛡️ **Guardrails anti-alucinación** para prevenir datos inventados
- 📅 **Gestión automática de citas** con confirmación en lenguaje natural
- 📄 **Descarga segura de documentos** con tokens JWT (15 min expiry)
- 🔐 **Sistema de autenticación** completo
- 🗄️ **Base de datos PostgreSQL** con Docker
- 🚀 **API REST completa** con FastAPI
- ⚡ **Frontend moderno** con Next.js + TypeScript

## 🛠️ Stack Tecnológico

| Tecnología | Propósito | Estado |
|------------|-----------|--------|
| **Next.js 15** | Frontend / UI | ✅ Implementado |
| **FastAPI** | Backend / API REST | ✅ Implementado |
| **LangGraph** | Orquestación de IA | ✅ Implementado |
| **Groq API** | LLM (llama-3.3-70b) | ✅ Implementado |
| **PostgreSQL** | Base de datos | ✅ Configurado |
| **Docker** | Containerización | ✅ Configurado |
| **JWT** | Autenticación segura | ✅ Implementado |
| **SQLAlchemy** | ORM | ✅ Implementado |

## 📁 Estructura del Proyecto

```
medical-ai-assistant/
├── backend/                    # Backend FastAPI
│   ├── main.py                # Punto de entrada
│   ├── run_backend.py         # Script de inicio con env vars
│   ├── config.py              # Configuración (JWT, uploads, DB)
│   ├── database.py            # Conexión PostgreSQL
│   ├── models.py              # Modelos de datos (ORM)
│   ├── requirements.txt       # Dependencias Python
│   ├── routers/               # Endpoints API
│   │   ├── auth.py           # Autenticación y login
│   │   ├── patients.py        # CRUD pacientes
│   │   ├── appointments.py    # Gestión de citas
│   │   ├── chat.py           # Chat con memoria conversacional
│   │   └── documents.py      # Descarga segura con JWT
│   ├── services/              # Lógica de negocio
│   │   └── ai_agent.py       # Agente IA (LangGraph + Groq)
│   └── uploads/              # Documentos médicos
├── frontend/                  # Frontend Next.js + TypeScript
│   ├── src/app/
│   │   ├── page.tsx          # Landing page
│   │   ├── login/            # Sistema de login
│   │   └── chat/             # Interfaz de chat
│   └── package.json
├── docker-compose.yml         # Configuración Docker
├── QUICKSTART.md             # Guía de inicio rápido
└── DOCKER.md                 # Documentación Docker
```

## 🚀 Inicio Rápido

### Prerequisitos

- **Python 3.12+** instalado
- **Docker Desktop** instalado y corriendo
- **Node.js 20+** (para el frontend, cuando esté listo)

### 1. Clonar el repositorio

```bash
cd e:\repositorios\R\medical-ai-assistant
```

### 2. Iniciar PostgreSQL con Docker

```bash
docker-compose up -d
```

Esto inicia:
- PostgreSQL en `localhost:5432`
- pgAdmin en `http://localhost:5050`

### 3. Configurar el backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
```

### 4. Ejecutar el backend

```bash
python main.py
```

### 5. Probar la API

Abre tu navegador:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **pgAdmin**: http://localhost:5050 (admin@medical-ai.com / admin)

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) - Guía de inicio rápido detallada
- [DOCKER.md](DOCKER.md) - Documentación completa de Docker
- [backend/README.md](backend/README.md) - Documentación del backend

## 🧪 Probar los Endpoints

### Crear un paciente
```bash
curl -X POST "http://localhost:8000/api/patients/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"juan@example.com\",\"name\":\"Juan Pérez\",\"phone\":\"555-1234\"}"
```

### Listar pacientes
```bash
curl http://localhost:8000/api/patients/
```

### Probar WebSocket (JavaScript en consola del navegador)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/juan@example.com');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
ws.send(JSON.stringify({content: "Necesito agendar una cita"}));
```

## 🗺️ Roadmap

### Fase 1: Backend Base ✅
- [x] Estructura del proyecto
- [x] FastAPI con endpoints básicos
- [x] PostgreSQL con Docker
- [x] Modelos de base de datos
- [x] Sistema de chat funcional

### Fase 2: Inteligencia IA ✅
- [x] Integrar LangGraph con StateGraph
- [x] Implementar agente conversacional Groq
- [x] Detección de intenciones (citas, documentos, historia)
- [x] Memoria conversacional (8 mensajes)
- [x] Guardrails anti-alucinación
- [x] Gestión automática de citas via IA
- [x] Reprogramación con confirmación

### Fase 3: Frontend ✅
- [x] Aplicación Next.js + TypeScript
- [x] Sistema de autenticación
- [x] Interfaz de chat funcional
- [x] Landing page
- [ ] Dashboard de pacientes
- [ ] Panel de gestión de citas
- [ ] Subida de documentos via UI

### Fase 4: Seguridad y Documentos ✅
- [x] Autenticación JWT
- [x] Descarga segura de documentos con tokens
- [x] Sistema de permisos por paciente
- [ ] Roles y permisos avanzados
- [ ] Notificaciones por email

### Fase 5: Producción 🔜
- [ ] Deploy con Docker Compose completo
- [ ] Tests automatizados
- [ ] CI/CD pipeline
- [ ] Monitoreo y logs
- [ ] Backup automático de BD

## 🔧 Comandos Útiles

### Docker
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose stop

# Reiniciar servicios
docker-compose restart

# Eliminar todo (⚠️ borra datos)
docker-compose down -v
```

### Backend
```bash
cd backend

# Activar entorno virtual
.\venv\Scripts\activate

# Ejecutar servidor
python main.py

# O con uvicorn
uvicorn main:app --reload
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y de uso educacional.

## 👨‍💻 Autor

Desarrollado con ❤️ para revolucionar la atención médica con IA

## 🆘 Soporte

¿Problemas? Revisa:
1. [QUICKSTART.md](QUICKSTART.md) - Guía paso a paso
2. [DOCKER.md](DOCKER.md) - Solución de problemas con Docker
3. Verifica que Docker esté corriendo
4. Verifica que el puerto 8000 esté libre
