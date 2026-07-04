import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# CP-HU05-01 — test_crear_pedido_con_producto_disponible
def test_crear_pedido_con_producto_disponible():
    payload = {
        "id_mesa": 1,
        "detalles": [
            {
                "id_producto": 1,
                "cantidad_pedida": 2
            }
        ]
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["estado"].lower() == "pendiente"
    assert data["total_pago"] > 0

# CP-HU05-02 — test_crear_pedido_con_producto_no_disponible_debe_fallar
def test_crear_pedido_con_producto_no_disponible_debe_fallar():
    # 1. Desactivamos el producto ID 1 vía PUT
    client.put("/productos/1", json={"disponible": False})
    
    # 2. Intentamos pedir el producto desactivado
    payload = {
        "id_mesa": 1,
        "detalles": [
            {
                "id_producto": 1,
                "cantidad_pedida": 1
            }
        ]
    }
    response = client.post("/pedidos", json=payload)
    
    # Restauramos el producto para mantener la base de datos limpia para otros tests
    client.put("/productos/1", json={"disponible": True})
    
    # Aquí es donde se expone el BUG #004:
    # Debería responder 400 (Bad Request), pero el backend actual devuelve 201 porque no valida disponibilidad.
    # El assert fallará como pide el enunciado de tu caso de prueba.
    assert response.status_code == 400

# CP-HU05-03 — test_crear_pedido_con_mesa_inexistente_devuelve_404
def test_crear_pedido_con_mesa_inexistente_devuelve_404():
    payload = {
        "id_mesa": 9999,
        "detalles": [
            {
                "id_producto": 1,
                "cantidad_pedida": 1
            }
        ]
    }
    response = client.post("/pedidos", json=payload)
    assert response.status_code == 404

# CP-HU05-04 — test_obtener_pedido_por_id
def test_obtener_pedido_por_id():
    payload = {
        "id_mesa": 1,
        "detalles": [
            {
                "id_producto": 1,
                "cantidad_pedida": 1
            }
        ]
    }
    post_res = client.post("/pedidos", json=payload)
    assert post_res.status_code == 201
    data = post_res.json()
    id_pedido = data["id_pedido"]
    
    # Consultamos el ID retornado
    response = client.get(f"/pedidos/{id_pedido}")
    assert response.status_code == 200
    assert response.json()["id_pedido"] == id_pedido