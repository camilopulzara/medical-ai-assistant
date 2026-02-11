# Medical AI Assistant - Backend

Backend del asistente médico inteligente construido con FastAPI, LangGraph y PostgreSQL.

## 🚀 Inicio Rápido

### 1. Crear entorno virtual

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia `.env.example` a `.env` y configura tus credenciales:

```bash
copy .env.example .env
```

Edita `.env` con tus valores:
- `DATABASE_URL`: URL de tu PostgreSQL
- `SECRET_KEY`: Genera una clave segura
- `OPENAI_API_KEY`: Tu API key (opcional)

### 4. Iniciar PostgreSQL con Docker

Desde la raíz del proyecto:

```bash
docker-compose up -d
```

PostgreSQL estará disponible en `localhost:5432`. Ver [DOCKER.md](../DOCKER.md) para más detalles.

### 5. Ejecutar el servidor

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Documentación API

Una vez el servidor esté corriendo:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Estructura del Proyecto

```
backend/
├── main.py                 # Aplicación FastAPI principal
├── config.py              # Configuración y settings
├── database.py            # Conexión a PostgreSQL
├── models.py              # Modelos SQLAlchemy
├── requirements.txt       # Dependencias Python
├── .env.example          # Ejemplo de variables de entorno
├── routers/              # Endpoints organizados
│   ├── patients.py       # CRUD de pacientes
│   ├── appointments.py   # Gestión de citas
│   └── chat.py          # WebSocket para chat
└── services/            # Lógica de negocio (próximamente)
    └── ai_agent.py      # Integración LangGraph
```

## 🧪 Probar los Endpoints

### Crear un paciente

```bash
curl -X POST "http://localhost:8000/api/patients/" \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@example.com","name":"Juan Pérez","phone":"555-1234"}'
```

### Listar pacientes

```bash
curl "http://localhost:8000/api/patients/"
```

### Probar WebSocket (con websocat o desde navegador)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/juan@example.com');
ws.onmessage = (event) => console.log(event.data);
ws.send(JSON.stringify({content: "Hola"}));
```

## 🔧 Próximos Pasos

1. ✅ Backend básico funcionando
2. ⏳ Integrar LangGraph para conversaciones
3. ⏳ Implementar agente IA para gestión de citas
4. ⏳ Añadir autenticación JWT
5. ⏳ Subida de documentos médicos

## 🛠️ Tecnologías

- **FastAPI 0.109+**: Framework web
- **SQLAlchemy 2.0+**: ORM
- **PostgreSQL**: Base de datos
- **Pydantic**: Validación de datos
- **WebSockets**: Chat en tiempo real
- **LangGraph**: Orquestación de IA (próximamente)
