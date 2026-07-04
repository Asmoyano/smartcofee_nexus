import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# CP-HU14-01 — test_validar_qr_existente_retorna_mesa
def test_validar_qr_existente_retorna_mesa():
    # Intenta con MESA01, si en tu DB es QR_MESA_1 lo adaptamos
    response = client.get("/mesas/MESA01")
    if response.status_code == 404:
        response = client.get("/mesas/QR_MESA_1")
        
    assert response.status_code == 200
    data = response.json()
    assert "id_mesa" in data
    assert "qr_code" in data

# CP-HU14-02 — test_validar_qr_inexistente_devuelve_404
def test_validar_qr_inexistente_devuelve_404():
    response = client.get("/mesas/QR_FALSO_999")
    assert response.status_code == 404

# CP-HU14-03 — test_pedido_queda_vinculado_a_mesa_correcta
def test_pedido_queda_vinculado_a_mesa_correcta():
    payload = {
        "id_mesa": 1,
        "detalles": [
            {
                "id_producto": 2,
                "cantidad_pedida": 1
            }
        ]
    }
    post_res = client.post("/pedidos", json=payload)
    assert post_res.status_code == 201
    data_pedido = post_res.json()
    
    # Verificamos la consistencia de la llave foránea
    assert data_pedido["id_mesa"] == 1