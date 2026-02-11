from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker  
from config import settings
import time
import logging

logger = logging.getLogger(__name__)

# Crear engine de SQLAlchemy con configuración robusta
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)

# Sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(max_retries=5, delay=2):
    """Esperar a que la base de datos esté lista"""
    for i in range(max_retries):
        try:
            # Intentar conexión
            connection = engine.connect()
            connection.close()
            logger.info("✅ Base de datos conectada")
            return True
        except Exception as e:
            logger.warning(f"⏳ Esperando base de datos... intento {i+1}/{max_retries}")
            if i < max_retries - 1:
                time.sleep(delay)
            else:
                logger.error(f"❌ No se pudo conectar a la base de datos: {e}")
                raise
    return False


def init_db():
    """Inicializar base de datos y crear tablas"""
    try:
        wait_for_db()
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {e}")
        raise
