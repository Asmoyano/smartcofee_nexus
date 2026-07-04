"""
Tests Sprint 2 — HU06: Actualización de estado de pedidos en cocina
Cubre TA06-2 (PATCH /estado) y TA06-3 (auditoría de timestamps)
Todos los casos deben pasar — no hay bugs en HU06.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Mesa, Producto, Categoria, Insumo, Receta

import app.models as models 
from app.models import Mesa, Producto, Categoria, Insumo, Receta

# ─── Configuración de base de datos en memoria para testing ───────────────────
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"
engine_test = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()

    # Datos mínimos necesarios para crear pedidos
    categoria = Categoria(nombre="Cafés")
    db.add(categoria)
    db.commit()
    db.refresh(categoria)

    insumo = Insumo(
        nombre="Café molido",
        stock_actual=500.0,
        stock_minimo=50.0,
        unidad_medida="g",
        es_alergeno=False
    )
    db.add(insumo)
    db.commit()
    db.refresh(insumo)

    producto = Producto(
        id_categoria=categoria.id_categoria,
        nombre="Café Americano",
        precio=6.50,
        disponible=True
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)

    receta = Receta(
        id_producto=producto.id_producto,
        id_insumo=insumo.id_insumo,
        cantidad_usada=18.0
    )
    db.add(receta)

    mesa = Mesa(qr_code="QR_MESA_1")
    db.add(mesa)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine_test)


client = TestClient(app)


def _crear_pedido_base():
    """Helper: crea un pedido válido y retorna su ID."""
    db = TestingSessionLocal()
    mesa = db.query(Mesa).first()
    producto = db.query(Producto).first()
    db.close()

    res = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": producto.id_producto, "cantidad_pedida": 1}]
    })
    assert res.status_code == 201
    return res.json()["id_pedido"]


# ─── CP-HU06-01 ───────────────────────────────────────────────────────────────
def test_actualizar_estado_pendiente_a_en_preparacion():
    """
    CP-HU06-01: Verifica que PATCH /pedidos/{id}/estado transicione
    correctamente de 'pendiente' a 'en_preparacion' devolviendo HTTP 200.
    """
    id_pedido = _crear_pedido_base()

    res = client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})

    assert res.status_code == 200
    data = res.json()
    assert data["estado"] == "en_preparacion"
    assert data["id_pedido"] == id_pedido


# ─── CP-HU06-02 ───────────────────────────────────────────────────────────────
def test_actualizar_estado_en_preparacion_a_listo():
    """
    CP-HU06-02: Verifica la transición completa pendiente → en_preparacion → listo.
    TA06-4: Una vez marcado como listo, el estado debe reflejarse correctamente.
    """
    id_pedido = _crear_pedido_base()

    # Primera transición
    res1 = client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})
    assert res1.status_code == 200

    # Segunda transición
    res2 = client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "listo"})
    assert res2.status_code == 200
    data = res2.json()
    assert data["estado"] == "listo"


# ─── CP-HU06-03 ───────────────────────────────────────────────────────────────
def test_actualizar_estado_invalido_devuelve_422():
    """
    CP-HU06-03: Verifica que un estado no reconocido por el sistema
    devuelva HTTP 422 Unprocessable Entity con mensaje de error claro.
    """
    id_pedido = _crear_pedido_base()

    res = client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "cocinando_rapido"})

    assert res.status_code == 422


# ─── CP-HU06-04 ───────────────────────────────────────────────────────────────
def test_timestamp_auditoria_se_registra_al_iniciar_preparacion():
    """
    CP-HU06-04: Verifica que al transicionar a 'en_preparacion' el campo
    fecha_inicio_prep quede registrado (TA06-3 — auditoría de tiempos de cocina).
    """
    id_pedido = _crear_pedido_base()

    # Verificar que fecha_inicio_prep es null antes de la transición
    res_inicial = client.get(f"/pedidos/{id_pedido}")
    assert res_inicial.json()["fecha_inicio_prep"] is None

    # Transicionar a en_preparacion
    client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})

    # Verificar que fecha_inicio_prep ya tiene valor
    res_final = client.get(f"/pedidos/{id_pedido}")
    assert res_final.json()["fecha_inicio_prep"] is not None
