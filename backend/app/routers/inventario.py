from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Insumo, Pedido, Producto
from app.schemas import InsumoCreate, InsumoResponse

router = APIRouter(prefix="/inventario", tags=["Gestión de Inventario & Insumos"])


# ─── POST /inventario/insumos ─────────────────────────────────────────────────
@router.post("/insumos", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
def crear_insumo(payload: InsumoCreate, db: Session = Depends(get_db)):
    """
    TA09-3: Interfaz administrativa para registrar nuevos insumos en el inventario.
    """
    nuevo_insumo = Insumo(
        nombre=payload.nombre,
        stock_actual=payload.stock_actual,
        stock_minimo=payload.stock_minimo,
        unidad_medida=payload.unidad_medida,
        es_alergeno=payload.es_alergeno
    )
    db.add(nuevo_insumo)
    db.commit()
    db.refresh(nuevo_insumo)
    return nuevo_insumo


# ─── GET /inventario/tiempo-espera-estimado ──────────────────────────────────
@router.get("/tiempo-espera-estimado")
def obtener_tiempo_espera_estimado(db: Session = Depends(get_db)):
    """
    TA07-1: Calcula analíticamente la suma de tiempos estimado basándose
    en la cola FIFO actual de pedidos pendientes y en preparación.
    """
    pedidos_activos = db.query(Pedido).filter(
        Pedido.estado.in_(["pendiente", "en_preparacion"])
    ).count()
    
    tiempo_estimado = pedidos_activos * 5  # 5 minutos promedio por comanda
    return {"tiempo_estimado_minutos": max(5, tiempo_estimado)}


# ─── POST /inventario/descontar-pedido/{id} ───────────────────────────────────
@router.post("/descontar-pedido/{id_pedido}")
def descontar_stock_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """
    TA09-2: Dispara el descuento de insumos cuando una orden pasa a producción.
    
    BUG #001 (activo): Ejecuta los descuentos y guarda iteración por iteración 
    mediante db.commit() sueltos sin manejar una transacción atómica estructurada. 
    Si el proceso se interrumpe a la mitad, la base de datos queda corrupta e inconsistente.

    BUG #005 (activo): Evalúa 'stock_actual <= stock_minimo' bloqueando pedidos
    de forma errónea cuando el insumo está exactamente sobre el límite de alerta.
    """
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido con ID {id_pedido} no existe."
        )

    # Recorrer el detalle del pedido (BUG #001: Sin bloque transaccional unificado)
    for detalle in pedido.detalles:
        producto = db.query(Producto).filter(
            Producto.id_producto == detalle.id_producto
        ).first()

        # Consultar la receta del producto para extraer sus insumos asociados
        for receta in producto.recetas:
            insumo = db.query(Insumo).filter(
                Insumo.id_insumo == receta.id_insumo
            ).first()

            # BUG #005: Control de frontera erróneo '<=' en vez de '<'
            if insumo.stock_actual <= insumo.stock_minimo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Alerta Crítica de Stock: El insumo '{insumo.nombre}' alcanzó su nivel mínimo."
                )

            # Deducción del stock físico calculado
            cantidad_total_a_descontar = receta.cantidad_usada * detalle.cantidad_pedida
            insumo.stock_actual -= cantidad_total_a_descontar
            
            db.add(insumo)
            db.commit()  # Guardado fragmentado por ciclo (Causa raíz del BUG #001)

    return {"status": "Stock descontado exitosamente conforme a recetas del pedido"}