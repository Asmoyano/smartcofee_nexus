"""
Sprint 1 — HU01: Catálogo de productos
Resultado esperado: 4 passed
"""
from app.models import Producto


def test_listar_productos_devuelve_lista(client, db_session):
    """CP-HU01-01: GET /productos devuelve HTTP 200 y al menos un producto."""
    res = client.get("/productos")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


def test_filtrar_productos_por_categoria(client, db_session):
    """CP-HU01-02: GET /productos?categoria_id=1 devuelve solo productos de esa categoría."""
    res = client.get("/productos?categoria_id=1")
    assert res.status_code == 200
    data = res.json()
    assert all(p["id_categoria"] == 1 for p in data)


def test_obtener_detalle_producto_existente(client, db_session):
    """CP-HU01-03: GET /productos/{id} devuelve detalle con insumos incluidos."""
    producto = db_session.query(Producto).filter(Producto.disponible == True).first()
    res = client.get(f"/productos/{producto.id_producto}")
    assert res.status_code == 200
    data = res.json()
    assert "id_producto" in data
    assert "nombre"      in data
    assert "precio"      in data
    assert "insumos"     in data


def test_obtener_producto_inexistente_devuelve_404(client, db_session):
    """CP-HU01-04: GET /productos/9999 devuelve HTTP 404."""
    res = client.get("/productos/9999")
    assert res.status_code == 404
