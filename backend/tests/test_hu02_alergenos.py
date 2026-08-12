"""
Sprint 1 — HU02: Alertas de alérgenos en el catálogo
Resultado esperado: 3 passed
"""


def test_lista_productos_incluye_campo_es_alergeno(client, db_session):
    """CP-HU02-01: Todos los productos en la lista tienen el campo es_alergeno."""
    res = client.get("/productos")
    assert res.status_code == 200
    for p in res.json():
        assert "es_alergeno" in p


def test_producto_con_alergeno_muestra_true(client, db_session):
    """CP-HU02-02: Café Latte (tiene leche alérgena) devuelve es_alergeno: true."""
    res = client.get("/productos")
    latte = next((p for p in res.json() if "Latte" in p["nombre"]), None)
    assert latte is not None
    assert latte["es_alergeno"] == True


def test_producto_sin_alergenos_muestra_false(client, db_session):
    """CP-HU02-03: Espresso (solo café, no alérgeno) devuelve es_alergeno: false."""
    res = client.get("/productos")
    espresso = next((p for p in res.json() if p["nombre"] == "Espresso"), None)
    assert espresso is not None
    assert espresso["es_alergeno"] == False
