import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from database import init_db
from routers import patients, appointments, chat, auth, documents
import sys
import io
from pathlib import Path

# Configurar encoding UTF-8 correcto
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Crear aplicación FastAPI
app = FastAPI(
    title="Medical AI Assistant API",
    description="Backend para asistente medico inteligente",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Evento de inicio
@app.on_event("startup")
async def startup_event():
    """Inicializar base de datos al arrancar"""
    print("🚀 Iniciando servidor...")
    try:
        init_db()
        print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo inicializar BD: {e}")
        print("El servidor continuará pero los endpoints de BD no funcionarán")


# Ruta raíz
@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {
        "message": "Medical AI Assistant API",
        "status": "running",
        "version": "1.0.0"
    }


# Health check
@app.get("/health")
async def health_check():
    """Verificar estado del servidor"""
    return {"status": "healthy"}


# Incluir routers
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(documents.router)

# Servir archivos estáticos desde carpeta uploads
uploads_dir = Path(settings.UPLOADS_DIR)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")


# Punto de entrada
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
