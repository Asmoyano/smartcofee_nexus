import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# CP-HU02-01 (FALLARÁ con AssertionError)
def test_lista_productos_incluye_campo_es_alergeno():
    response = client.get("/productos")
    assert response.status_code == 200
    data = response.json()
    
    # Verifica que el campo exista en cada ítem
    for producto in data:
        assert "es_alergeno" in producto
        
    # El test espera que al menos uno sea True, pero fallará porque todos devuelven False
    lista_estados = [producto["es_alergeno"] for producto in data]
    assert True in lista_estados

# CP-HU02-02 (FALLARÁ con AssertionError)
def test_producto_con_alergeno_muestra_true():
    response = client.get("/productos")
    data = response.json()
    
    # Buscamos la Torta de Chocolate o Café Latte que sabemos que lleva alérgenos por el seed
    producto_con_alergeno = next((p for p in data if "Torta" in p["nombre"] or "Latte" in p["nombre"]), None)
    
    assert producto_con_alergeno is not None
    # Fallará aquí porque el Bug #003 fuerza un False en la lista general
    assert producto_con_alergeno["es_alergeno"] is True

# CP-HU02-03 (PASA ✅ debido al bug)
def test_producto_sin_alergenos_muestra_false():
    response = client.get("/productos")
    data = response.json()
    
    # Buscamos un producto limpio de alérgenos (Ej. Espresso)
    producto_sin_alergeno = next((p for p in data if "Espresso" in p["nombre"]), None)
    
    if producto_sin_alergeno:
        assert producto_sin_alergeno["es_alergeno"] is False
    else:
        # Si no lo encuentra por nombre, cualquier producto dará False por el bug, así que pasa.
        assert data[0]["es_alergeno"] is False