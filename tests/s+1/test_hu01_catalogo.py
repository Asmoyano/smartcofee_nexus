import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# CP-HU01-01
def test_listar_productos_devuelve_lista():
    response = client.get("/productos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# CP-HU01-02
def test_filtrar_productos_por_categoria():
    # Asumiendo que la categoría 1 existe debido al seed
    response = client.get("/productos?categoria_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Validamos que todos correspondan a la categoría solicitada
    for producto in data:
        assert producto.get("categoria_id") == 1 or producto.get("id_categoria") == 1

# CP-HU01-03
def test_obtener_detalle_producto_existente():
    # Consultamos el ID 1 inyectado por el seed
    response = client.get("/productos/1")
    assert response.status_code == 200
    data = response.json()
    assert "id_producto" in data or "id" in data
    assert "nombre" in data
    assert "precio" in data
    assert "insumos" in data  # La respuesta extendida que agregamos en schemas
    assert isinstance(data["insumos"], list)

# CP-HU01-04
def test_obtener_producto_inexistente_devuelve_404():
    response = client.get("/productos/9999")
    assert response.status_code == 404