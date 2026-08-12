"""
Sprint 2 — HU06: Actualización de estados en cocina
Resultado esperado: 4 passed
"""
from app.models import Mesa, Producto


def _crear_pedido(client, db_session):
    mesa     = db_session.query(Mesa).first()
    producto = db_session.query(Producto).filter(Producto.disponible == True).first()
    res = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": producto.id_producto, "cantidad_pedida": 1}]
    })
    assert res.status_code == 201
    return res.json()["id_pedido"]


def test_actualizar_estado_pendiente_a_en_preparacion(client, db_session):
    """CP-HU06-01: PATCH /pedidos/{id}/estado cambia a en_preparacion correctamente."""
    id_pedido = _crear_pedido(client, db_session)
    res = client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})
    assert res.status_code == 200
    assert res.json()["estado"] == "en_preparacion"


def test_actualizar_estado_en_preparacion_a_listo(client, db_session):
    """CP-HU06-02: Transición completa pendiente → en_preparacion → listo."""
    id_pedido = _crear_pedido(client, db_session)
    client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})
    res = client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "listo"})
    assert res.status_code == 200
    assert res.json()["estado"] == "listo"


def test_actualizar_estado_invalido_devuelve_422(client, db_session):
    """CP-HU06-03: Estado no reconocido devuelve HTTP 422."""
    id_pedido = _crear_pedido(client, db_session)
    res = client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "volando"})
    assert res.status_code == 422


def test_timestamp_auditoria_se_registra(client, db_session):
    """CP-HU06-04: fecha_inicio_prep se registra al pasar a en_preparacion."""
    id_pedido = _crear_pedido(client, db_session)
    assert client.get(f"/pedidos/{id_pedido}").json()["fecha_inicio_prep"] is None
    client.patch(f"/pedidos/{id_pedido}/estado", json={"estado": "en_preparacion"})
    assert client.get(f"/pedidos/{id_pedido}").json()["fecha_inicio_prep"] is not None
