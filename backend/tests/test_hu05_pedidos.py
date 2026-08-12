"""
Sprint 1 — HU05: Creación y consulta de pedidos
Resultado esperado: 4 passed
"""
from app.models import Mesa, Producto


def test_crear_pedido_con_producto_disponible(client, db_session):
    """CP-HU05-01: POST /pedidos crea pedido correctamente con HTTP 201."""
    mesa     = db_session.query(Mesa).first()
    producto = db_session.query(Producto).filter(Producto.disponible == True).first()

    res = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": producto.id_producto, "cantidad_pedida": 2}]
    })

    assert res.status_code == 201
    data = res.json()
    assert data["estado"] == "pendiente"
    assert data["total_pago"] > 0


def test_crear_pedido_con_producto_no_disponible_debe_fallar(client, db_session):
    """CP-HU05-02: POST /pedidos con producto no disponible devuelve HTTP 400."""
    mesa     = db_session.query(Mesa).first()
    no_disp  = db_session.query(Producto).filter(Producto.disponible == False).first()

    res = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": no_disp.id_producto, "cantidad_pedida": 1}]
    })

    assert res.status_code == 400


def test_crear_pedido_con_mesa_inexistente_devuelve_404(client, db_session):
    """CP-HU05-03: POST /pedidos con mesa inválida devuelve HTTP 404."""
    producto = db_session.query(Producto).filter(Producto.disponible == True).first()

    res = client.post("/pedidos", json={
        "id_mesa": 9999,
        "detalles": [{"id_producto": producto.id_producto, "cantidad_pedida": 1}]
    })

    assert res.status_code == 404


def test_obtener_pedido_por_id(client, db_session):
    """CP-HU05-04: GET /pedidos/{id} devuelve el pedido creado correctamente."""
    mesa     = db_session.query(Mesa).first()
    producto = db_session.query(Producto).filter(Producto.disponible == True).first()

    crear = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": producto.id_producto, "cantidad_pedida": 1}]
    })
    id_pedido = crear.json()["id_pedido"]

    res = client.get(f"/pedidos/{id_pedido}")
    assert res.status_code == 200
    assert res.json()["id_pedido"] == id_pedido
