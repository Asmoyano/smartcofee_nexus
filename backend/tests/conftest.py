import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import (
    Categoria, Insumo, Producto, Receta,
    Mesa, Usuario, Cliente
)

# StaticPool es crítico para SQLite en memoria con FastAPI.
# Sin él, cada conexión ve una base de datos diferente y las tablas
# creadas en el fixture no son visibles cuando el TestClient hace requests.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function")
def db_session():
    """
    Crea todas las tablas y datos de prueba antes de cada test.
    Los destruye completamente al terminar — cada test arranca limpio.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # ── Seed completo (Sprint 1 y Sprint 2) ───────────────────────────────────
    cat_cafes   = Categoria(nombre="Cafés")
    cat_postres = Categoria(nombre="Postres")
    db.add_all([cat_cafes, cat_postres])
    db.commit()

    ins_cafe   = Insumo(nombre="Café en grano",   stock_actual=1000.0, stock_minimo=200.0,  unidad_medida="g",  es_alergeno=False)
    ins_leche  = Insumo(nombre="Leche entera",    stock_actual=5000.0, stock_minimo=1000.0, unidad_medida="ml", es_alergeno=True)
    ins_harina = Insumo(nombre="Harina de trigo", stock_actual=2000.0, stock_minimo=500.0,  unidad_medida="g",  es_alergeno=True)
    ins_azucar = Insumo(nombre="Azúcar rubia",    stock_actual=3000.0, stock_minimo=300.0,  unidad_medida="g",  es_alergeno=False)
    ins_limite = Insumo(nombre="Insumo Límite",   stock_actual=100.0,  stock_minimo=100.0,  unidad_medida="u",  es_alergeno=False)
    db.add_all([ins_cafe, ins_leche, ins_harina, ins_azucar, ins_limite])
    db.commit()

    p1 = Producto(id_categoria=cat_cafes.id_categoria,   nombre="Espresso",           descripcion="Café cargado e intenso",       precio=6.50,  disponible=True)
    p2 = Producto(id_categoria=cat_cafes.id_categoria,   nombre="Café Latte",         descripcion="Espresso con leche al vapor",  precio=8.50,  disponible=True)
    p3 = Producto(id_categoria=cat_postres.id_categoria, nombre="Torta de Chocolate", descripcion="Porción de torta húmeda",      precio=12.00, disponible=True)
    p4 = Producto(id_categoria=cat_cafes.id_categoria,   nombre="Capuccino Especial", descripcion="Edición limitada de temporada",precio=10.50, disponible=False)
    db.add_all([p1, p2, p3, p4])
    db.commit()

    db.add_all([
        Receta(id_producto=p1.id_producto, id_insumo=ins_cafe.id_insumo,   cantidad_usada=18.0),
        Receta(id_producto=p2.id_producto, id_insumo=ins_cafe.id_insumo,   cantidad_usada=18.0),
        Receta(id_producto=p2.id_producto, id_insumo=ins_leche.id_insumo,  cantidad_usada=200.0),
        Receta(id_producto=p3.id_producto, id_insumo=ins_harina.id_insumo, cantidad_usada=150.0),
        Receta(id_producto=p3.id_producto, id_insumo=ins_azucar.id_insumo, cantidad_usada=50.0),
    ])
    db.add_all([
        Mesa(qr_code="QR_MESA_1"),
        Mesa(qr_code="QR_MESA_2"),
        Mesa(qr_code="QR_MESA_3"),
    ])
    db.add_all([
        Usuario(nombre="Admin",   rol="admin",    password_hash="admin123"),
        Usuario(nombre="Cocinero",rol="cocinero", password_hash="cocina123"),
        Cliente(nombre="Cliente Test", correo="test@test.com", documento_identidad="12345678"),
    ])
    db.commit()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Reemplaza la dependencia get_db de producción por la sesión de test.
    Garantiza que todos los endpoints usen la base de datos en memoria.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
