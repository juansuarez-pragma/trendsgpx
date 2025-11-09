"""
Configuración base de SQLAlchemy
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Obtener DATABASE_URL de variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://trendsgpx:password@localhost:5432/trendsgpx")

# Crear engine
# Para producción con muchas conexiones concurrentes, usar pool
# Para desarrollo o workers Celery, puede ser beneficioso NullPool
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Logging de SQL
)

# Crear sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos declarativos
Base = declarative_base()


def get_db():
    """
    Dependency para FastAPI que proporciona sesión de base de datos.
    Uso:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
