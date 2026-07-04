from app.database import SessionLocal, engine, Base
from app.models import Categoria, Insumo, Producto, Receta, Mesa, Usuario, Cliente

def seed_data():
    db = SessionLocal()
    try:
        print("Limpiando datos existentes...")
        # Limpieza ordenada respetando llaves foráneas
        db.query(Receta).delete()
        db.query(Producto).delete()
        db.query(Categoria).delete()
        db.query(Insumo).delete()
        db.query(Mesa).delete()
        db.query(Usuario).delete()
        db.query(Cliente).delete()
        db.commit()

        print("Insertando categorías...")
        cat_cafes = Categoria(nombre="Cafés")
        cat_postres = Categoria(nombre="Postres")
        db.add_all([cat_cafes, cat_postres])
        db.commit()  # Commiteamos para generar los IDs de las categorías

        print("Insertando insumos (con configuración de alérgenos y stock)...")
        # Insumos normales y alérgenos para el Bug #003
        ins_cafe = Insumo(nombre="Café en grano", stock_actual=1000.0, stock_minimo=200.0, unidad_medida="gramos", es_alergeno=False)
        ins_leche = Insumo(nombre="Leche entera", stock_actual=5000.0, stock_minimo=1000.0, unidad_medida="ml", es_alergeno=True) # Alérgeno (Lactosa)
        ins_harina = Insumo(nombre="Harina de trigo", stock_actual=2000.0, stock_minimo=500.0, unidad_medida="gramos", es_alergeno=True) # Alérgeno (Gluten)
        ins_azucar = Insumo(nombre="Azúcar rubia", stock_actual=3000.0, stock_minimo=300.0, unidad_medida="gramos", es_alergeno=False)
        
        # Insumo crítico exacto para probar el límite del Bug #005 más adelante
        ins_limite = Insumo(nombre="Insumo Límite", stock_actual=100.0, stock_minimo=100.0, unidad_medida="unidades", es_alergeno=False)

        db.add_all([ins_cafe, ins_leche, ins_harina, ins_azucar, ins_limite])
        db.commit()

        print("Insertando productos...")
        # Productos para HU01, HU02 y escenarios de borde (Bug #004)
        p1 = Producto(id_categoria=cat_cafes.id_categoria, nombre="Espresso", descripcion="Café cargado e intenso", precio=6.50, disponible=True)
        p2 = Producto(id_categoria=cat_cafes.id_categoria, nombre="Café Latte", descripcion="Espresso con leche al vapor", precio=8.50, disponible=True) # Contiene alérgeno (Leche)
        p3 = Producto(id_categoria=cat_postres.id_categoria, nombre="Torta de Chocolate", descripcion="Porción de torta húmeda", precio=12.00, disponible=True) # Contiene alérgeno (Harina)
        
        # Producto inyectado explícitamente como NO DISPONIBLE para cazar el Bug #004
        p_no_disp = Producto(id_categoria=cat_cafes.id_categoria, nombre="Capuccino Especial", descripcion="Edición limitada agotada", precio=10.50, disponible=False)

        db.add_all([p1, p2, p3, p_no_disp])
        db.commit()

        print("Insertando recetas (relación productos e insumos)...")
        # Espresso usa 18g de café
        r1 = Receta(id_producto=p1.id_producto, id_insumo=ins_cafe.id_insumo, cantidad_usada=18.0)
        
        # Latte usa 18g de café y 200ml de leche (Alérgeno)
        r2_1 = Receta(id_producto=p2.id_producto, id_insumo=ins_cafe.id_insumo, cantidad_usada=18.0)
        r2_2 = Receta(id_producto=p2.id_producto, id_insumo=ins_leche.id_insumo, cantidad_usada=200.0)
        
        # Torta usa 150g de harina (Alérgeno) y 50g de azúcar
        r3_1 = Receta(id_producto=p3.id_producto, id_insumo=ins_harina.id_insumo, cantidad_usada=150.0)
        r3_2 = Receta(id_producto=p3.id_producto, id_insumo=ins_azucar.id_insumo, cantidad_usada=50.0)

        db.add_all([r1, r2_1, r2_2, r3_1, r3_2])
        db.commit()

        print("Insertando mesas y códigos QR...")
        # Mesas fijas para HU14
        m1 = Mesa(qr_code="QR_MESA_1")
        m2 = Mesa(qr_code="QR_MESA_2")
        m3 = Mesa(qr_code="QR_MESA_3")
        db.add_all([m1, m2, m3])

        print("Insertando usuarios de prueba...")
        # Usuarios base (sin encriptar fuerte aún para pruebas simples de desarrollo)
        u1 = Usuario(nombre="Carlos (Admin)", rol="admin", password_hash="admin123")
        u2 = Usuario(nombre="Ana (Cocinera)", rol="cocinero", password_hash="cocina123")
        u3 = Usuario(nombre="Luis (Mesero)", rol="mesero", password_hash="mesero123")
        db.add_all([u1, u2, u3])

        print("Insertando clientes base...")
        c1 = Cliente(nombre="Adolfo Moyano", correo="adolfo@example.com", documento_identidad="77777777")
        db.add_all([c1])

        db.commit()
        print("¡Base de datos populada exitosamente con escenarios de prueba (OK)!")

    except Exception as e:
        db.rollback()
        print(f"Error al poblar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_data()