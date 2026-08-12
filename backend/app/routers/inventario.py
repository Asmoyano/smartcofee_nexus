from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Insumo, Pedido, Producto, Receta
from app.schemas import InsumoCreate, InsumoResponse, InsumoUpdate

router = APIRouter(prefix="/inventario", tags=["Gestión de Inventario & Insumos"])


# ─── GET /inventario ──────────────────────────────────────────────────────────
@router.get("", response_model=List[InsumoResponse])
def listar_inventario(db: Session = Depends(get_db)):
    """
    HU09: Lista todos los insumos con stock actual y flag de alerta.
    Un insumo está en alerta cuando stock_actual < stock_minimo.
    """
    insumos = db.query(Insumo).all()
    resultado = []
    for ins in insumos:
        resultado.append(InsumoResponse(
            id_insumo=ins.id_insumo,
            nombre=ins.nombre,
            stock_actual=ins.stock_actual,
            stock_minimo=ins.stock_minimo,
            unidad_medida=ins.unidad_medida,
            es_alergeno=ins.es_alergeno
        ))
    return resultado


# ─── GET /inventario/alertas ──────────────────────────────────────────────────
@router.get("/alertas")
def obtener_alertas_stock(db: Session = Depends(get_db)):
    """
    HU10 / TA10-1: Devuelve únicamente los insumos en nivel crítico.
    Alerta cuando stock_actual < stock_minimo (estrictamente menor).
    """
    insumos = db.query(Insumo).all()
    alertas = []
    for ins in insumos:
        if ins.stock_actual < ins.stock_minimo:
            alertas.append({
                "id_insumo": ins.id_insumo,
                "nombre": ins.nombre,
                "stock_actual": ins.stock_actual,
                "stock_minimo": ins.stock_minimo,
                "unidad_medida": ins.unidad_medida,
                "deficit": round(ins.stock_minimo - ins.stock_actual, 2)
            })
    return alertas


# ─── GET /inventario/tiempo-espera-estimado ───────────────────────────────────
@router.get("/tiempo-espera-estimado")
def obtener_tiempo_espera_estimado(db: Session = Depends(get_db)):
    """
    TA07-1: Calcula el tiempo estimado de espera basado en la cola FIFO actual.
    """
    pedidos_activos = db.query(Pedido).filter(
        Pedido.estado.in_(["pendiente", "en_preparacion"])
    ).count()
    tiempo_estimado = pedidos_activos * 5
    return {"tiempo_estimado_minutos": max(5, tiempo_estimado)}


# ─── GET /inventario/{id} ─────────────────────────────────────────────────────
@router.get("/{id_insumo}", response_model=InsumoResponse)
def obtener_insumo(id_insumo: int, db: Session = Depends(get_db)):
    insumo = db.query(Insumo).filter(Insumo.id_insumo == id_insumo).first()
    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insumo con ID {id_insumo} no encontrado."
        )
    return insumo


# ─── PUT /inventario/{id} ─────────────────────────────────────────────────────
@router.put("/{id_insumo}", response_model=InsumoResponse)
def actualizar_insumo(
    id_insumo: int,
    payload: InsumoUpdate,
    db: Session = Depends(get_db)
):
    """
    HU09 / TA09-3: Actualiza el stock o configuración de un insumo.
    Usado para reposición de inventario desde el panel administrativo.
    """
    insumo = db.query(Insumo).filter(Insumo.id_insumo == id_insumo).first()
    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insumo con ID {id_insumo} no encontrado."
        )
    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(insumo, campo, valor)
    db.commit()
    db.refresh(insumo)
    return insumo


# ─── POST /inventario/insumos ─────────────────────────────────────────────────
@router.post("/insumos", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
def crear_insumo(payload: InsumoCreate, db: Session = Depends(get_db)):
    """TA09-3: Registra un nuevo insumo en el inventario."""
    nuevo = Insumo(
        nombre=payload.nombre,
        stock_actual=payload.stock_actual,
        stock_minimo=payload.stock_minimo,
        unidad_medida=payload.unidad_medida,
        es_alergeno=payload.es_alergeno
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ─── POST /inventario/descontar-pedido/{id} ───────────────────────────────────
@router.post("/descontar-pedido/{id_pedido}")
def descontar_stock_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """
    HU09 / TA09-2: Descuenta automáticamente el stock de insumos
    basándose en las recetas de cada producto del pedido.
    Se dispara cuando el cocinero marca un pedido como 'listo'.
    """
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con ID {id_pedido} no existe."
        )

    resumen = []
    try:
        for detalle in pedido.detalles:
            producto = db.query(Producto).filter(
                Producto.id_producto == detalle.id_producto
            ).first()
            if not producto:
                continue

            for receta in producto.recetas:
                insumo = db.query(Insumo).filter(
                    Insumo.id_insumo == receta.id_insumo
                ).first()
                if not insumo:
                    continue

                cantidad_a_descontar = receta.cantidad_usada * detalle.cantidad_pedida

                if insumo.stock_actual < cantidad_a_descontar:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Stock insuficiente para '{insumo.nombre}'. "
                               f"Disponible: {insumo.stock_actual} {insumo.unidad_medida}."
                    )

                insumo.stock_actual = round(
                    insumo.stock_actual - cantidad_a_descontar, 4
                )
                resumen.append({
                    "insumo": insumo.nombre,
                    "descontado": cantidad_a_descontar,
                    "stock_restante": insumo.stock_actual
                })

        # Commit único al final — operación atómica
        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descontar stock: {str(e)}"
        )

    return {
        "mensaje": f"Stock descontado correctamente para pedido #{id_pedido}",
        "detalle": resumen
    }