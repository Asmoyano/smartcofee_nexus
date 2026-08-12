"""
Sprint 2 — HU09: Gestión de inventario y descuento automático de stock
Resultado esperado: 5 passed
"""
from app.models import Mesa, Producto, Insumo


def _crear_pedido_listo(client, db_session):
    mesa     = db_session.query(Mesa).first()
    espresso = db_session.query(Producto).filter(Producto.nombre == "Espresso").first()
    res = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": espresso.id_producto, "cantidad_pedida": 2}]
    })
    assert res.status_code == 201
    id_pedido = res.json()["id_pedido"]
    client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})
    client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "listo"})
    return id_pedido


def test_listar_inventario_devuelve_insumos(client, db_session):
    """CP-HU09-01: GET /inventario devuelve lista de insumos con campos correctos."""
    res = client.get("/inventario")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    for ins in data:
        assert "id_insumo"    in ins
        assert "stock_actual" in ins
        assert "stock_minimo" in ins


def test_insumo_bajo_minimo_aparece_en_alertas(client, db_session):
    """CP-HU09-02: Insumo con stock < mínimo aparece en GET /inventario/alertas."""
    leche = db_session.query(Insumo).filter(Insumo.nombre == "Leche entera").first()
    leche.stock_actual = 0.0
    db_session.commit()

    res = client.get("/inventario/alertas")
    assert res.status_code == 200
    assert any(a["nombre"] == "Leche entera" for a in res.json())


def test_insumo_igual_al_minimo_no_es_alerta(client, db_session):
    """CP-HU09-03: Insumo con stock == mínimo NO aparece en alertas (condición estricta <)."""
    res = client.get("/inventario/alertas")
    assert res.status_code == 200
    assert not any(a["nombre"] == "Insumo Límite" for a in res.json())


def test_descuento_automatico_reduce_stock(client, db_session):
    """CP-HU09-04: 2 Espressos × 18g = 36g descontados de Café en grano."""
    cafe = db_session.query(Insumo).filter(Insumo.nombre == "Café en grano").first()
    stock_antes = cafe.stock_actual

    id_pedido = _crear_pedido_listo(client, db_session)
    res = client.post(f"/inventario/descontar-pedido/{id_pedido}")
    assert res.status_code == 200

    db_session.expire_all()
    cafe_after = db_session.query(Insumo).filter(Insumo.nombre == "Café en grano").first()
    assert round(stock_antes - cafe_after.stock_actual, 2) == 36.0


def test_actualizar_stock_insumo(client, db_session):
    """CP-HU09-05: PUT /inventario/{id} actualiza el stock correctamente."""
    cafe = db_session.query(Insumo).filter(Insumo.nombre == "Café en grano").first()
    res  = client.put(f"/inventario/{cafe.id_insumo}", json={"stock_actual": 2000.0})
    assert res.status_code == 200
    assert res.json()["stock_actual"] == 2000.0
