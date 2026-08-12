"""
Sprint 1 — HU14: Validación de QR y vinculación de mesa
Resultado esperado: 3 passed
"""
from app.models import Mesa, Producto


def test_validar_qr_existente_retorna_mesa(client, db_session):
    """CP-HU14-01: GET /mesas/QR_MESA_1 devuelve HTTP 200 con datos de la mesa."""
    res = client.get("/mesas/QR_MESA_1")
    assert res.status_code == 200
    data = res.json()
    assert "id_mesa"  in data
    assert "qr_code"  in data
    assert data["qr_code"] == "QR_MESA_1"


def test_validar_qr_inexistente_devuelve_404(client, db_session):
    """CP-HU14-02: GET /mesas/QR_FALSO devuelve HTTP 404."""
    res = client.get("/mesas/QR_FALSO_999")
    assert res.status_code == 404


def test_pedido_queda_vinculado_a_mesa_correcta(client, db_session):
    """CP-HU14-03: El pedido creado tiene el id_mesa correcto en la respuesta."""
    mesa     = db_session.query(Mesa).filter(Mesa.qr_code == "QR_MESA_1").first()
    producto = db_session.query(Producto).filter(Producto.disponible == True).first()

    res = client.post("/pedidos", json={
        "id_mesa": mesa.id_mesa,
        "detalles": [{"id_producto": producto.id_producto, "cantidad_pedida": 1}]
    })

    assert res.status_code == 201
    assert res.json()["id_mesa"] == mesa.id_mesa
