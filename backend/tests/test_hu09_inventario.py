"""
Tests Sprint 2 — HU09: Gestión de inventario y descuento automático de stock
Cubre TA09-2 (descuento automático), TA09-3 (gestión de insumos), Bug #005.
Resultado esperado: 4 pass, 1 fail (CP-HU09-03 → Bug #005)
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

    categoria = Categoria(nombre="Cafés")
    db.add(categoria)
    db.commit()
    db.refresh(categoria)

    # Insumo con stock normal — no debería estar en alerta
    db.add(Insumo(
        nombre="Café molido",
        stock_actual=500.0,
        stock_minimo=50.0,
        unidad_medida="g",
        es_alergeno=False
    ))

    # Insumo con stock por debajo del mínimo — debe estar en alerta
    db.add(Insumo(
        nombre="Leche entera",
        stock_actual=30.0,
        stock_minimo=100.0,
        unidad_medida="ml",
        es_alergeno=True
    ))

    # Insumo con stock exactamente igual al mínimo
    # CP-HU09-03: con Bug #005 activo, este también aparecerá en alerta (incorrecto)
    db.add(Insumo(
        nombre="Azúcar",
        stock_actual=200.0,
        stock_minimo=200.0,
        unidad_medida="g",
        es_alergeno=False
    ))
    db.commit()

    # Insumo para prueba de descuento automático
    insumo_cafe = db.query(Insumo).filter(Insumo.nombre == "Café molido").first()

    producto = Producto(
        id_categoria=categoria.id_categoria,
        nombre="Café Americano",
        precio=6.50,
        disponible=True
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)

    db.add(Receta(
        id_producto=producto.id_producto,
        id_insumo=insumo_cafe.id_insumo,
        cantidad_usada=18.0
    ))

    mesa = Mesa(qr_code="QR_MESA_1")
    db.add(mesa)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine_test)


client = TestClient(app)


def _crear_y_marcar_listo():
    """
    Helper: crea un pedido, lo pasa a en_preparacion y luego a listo.
    Retorna el id_pedido para usarlo en el descuento de stock.
    """
    db = TestingSessionLocal()
    mesa = db.query(Mesa).first()
    producto = db.query(Producto).first()
    db.close()

    res = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": producto.id_producto, "cantidad_pedida": 2}]
    })
    assert res.status_code == 201
    id_pedido = res.json()["id_pedido"]

    client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})
    client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "listo"})
    return id_pedido


# ─── CP-HU09-01 ───────────────────────────────────────────────────────────────
def test_listar_inventario_devuelve_insumos_con_alerta():
    """
    CP-HU09-01: GET /inventario devuelve todos los insumos con sus campos
    stock_actual, stock_minimo y el campo calculado en_alerta.
    """
    res = client.get("/inventario")

    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Verificar que cada insumo tiene los campos requeridos
    for insumo in data:
        assert "id_insumo" in insumo
        assert "stock_actual" in insumo
        assert "stock_minimo" in insumo
        assert "en_alerta" in insumo


# ─── CP-HU09-02 ───────────────────────────────────────────────────────────────
def test_insumo_bajo_minimo_aparece_en_alerta():
    """
    CP-HU09-02: Verifica que el insumo 'Leche entera' (stock 30 < mínimo 100)
    aparezca correctamente marcado como en_alerta: true.
    """
    res = client.get("/inventario")
    assert res.status_code == 200

    leche = next((i for i in res.json() if i["nombre"] == "Leche entera"), None)
    assert leche is not None
    assert leche["en_alerta"] == True


# ─── CP-HU09-03 ───────────────────────────────────────────────────────────────
def test_insumo_igual_al_minimo_no_debe_estar_en_alerta():
    """
    CP-HU09-03: Verifica que el insumo 'Azúcar' (stock 200 == mínimo 200)
    NO esté en alerta — el criterio dice "por DEBAJO del mínimo".

    RESULTADO ESPERADO: FAIL → Bug #005
    El endpoint usa '<=' en vez de '<', por lo que marca en_alerta: true
    cuando stock_actual == stock_minimo, violando el criterio de aceptación.

    AssertionError esperado: assert True == False
    (el sistema devuelve en_alerta: True cuando debería ser False)
    """
    res = client.get("/inventario")
    assert res.status_code == 200

    azucar = next((i for i in res.json() if i["nombre"] == "Azúcar"), None)
    assert azucar is not None
    # Esta aserción FALLARÁ con Bug #005 activo
    assert azucar["en_alerta"] == False


# ─── CP-HU09-04 ───────────────────────────────────────────────────────────────
def test_descuento_automatico_reduce_stock_correctamente():
    """
    CP-HU09-04 / TA09-2 / TA09-4: Verifica que al disparar el descuento
    automático de un pedido con 2 Cafés Americanos (18g c/u = 36g total),
    el stock del insumo 'Café molido' baje exactamente 36g (de 500g a 464g).
    """
    # Stock inicial del café molido
    res_inicial = client.get("/inventario")
    cafe_inicial = next(
        (i for i in res_inicial.json() if i["nombre"] == "Café molido"), None
    )
    stock_antes = cafe_inicial["stock_actual"]

    # Crear pedido con 2 cafés y marcarlo como listo
    id_pedido = _crear_y_marcar_listo()

    # Disparar descuento automático (TA09-2)
    res_descuento = client.post(f"/inventario/descontar-pedido/{id_pedido}")
    assert res_descuento.status_code == 200

    # Verificar que el stock bajó exactamente 36g (18g × 2 unidades)
    res_final = client.get("/inventario")
    cafe_final = next(
        (i for i in res_final.json() if i["nombre"] == "Café molido"), None
    )
    stock_despues = cafe_final["stock_actual"]

    assert round(stock_antes - stock_despues, 2) == 36.0


# ─── CP-HU09-05 ───────────────────────────────────────────────────────────────
def test_actualizar_stock_insumo_correctamente():
    """
    CP-HU09-05: PUT /inventario/{id} actualiza el stock_actual de un insumo.
    Simula una reposición de inventario por parte del administrador.
    """
    db = TestingSessionLocal()
    insumo = db.query(Insumo).filter(Insumo.nombre == "Café molido").first()
    id_insumo = insumo.id_insumo
    db.close()

    res = client.put(f"/inventario/{id_insumo}", json={"stock_actual": 1000.0})

    assert res.status_code == 200
    data = res.json()
    assert data["stock_actual"] == 1000.0
    assert data["id_insumo"] == id_insumo
