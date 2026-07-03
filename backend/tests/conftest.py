import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# 1. Configurar una base de datos SQLite en memoria exclusiva para los Tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Fixture que crea las tablas antes de cada test y las destruye al finalizar."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture que reemplaza la dependencia de la BD de producción por la de pruebas."""
    def _get_db_override():
        try:
            yield db_session
        finally:
            pass
            
    # Inyectamos la BD en memoria en la aplicación de FastAPI
    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    # Limpiamos las modificaciones de dependencias al terminar el test
    app.dependency_overrides.clear()