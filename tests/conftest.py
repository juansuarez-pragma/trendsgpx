"""
Configuración de pytest y fixtures comunes
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.models.base import Base, get_db
from src.api.main import app
from src.utils.config import settings


# URL de base de datos de test (usar SQLite en memoria)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """
    Crea un engine de SQLAlchemy para tests.
    Usa SQLite en memoria para velocidad y aislamiento.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},  # Necesario para SQLite
    )

    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    yield engine

    # Limpiar después del test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Crea una sesión de base de datos para tests.
    Cada test obtiene una sesión limpia.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Crea un cliente de test de FastAPI.
    Sobrescribe la dependencia get_db para usar la sesión de test.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Limpiar override
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """
    Headers de autenticación para tests.
    Usa la API key configurada en settings.
    """
    return {"X-API-Key": settings.api_key}
